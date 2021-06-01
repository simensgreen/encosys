from concurrent.futures import ThreadPoolExecutor
import logging
from ._entity import EntityBuilder, Entity
from ._system import System
import typing

log = logging.getLogger(__name__)


class World:
    """
    Objects of this class store entity components, entities, define their relationships and call systems on demand
    """
    def __init__(self):
        self.__systems = set()
        self.__archetypes = dict()
        self.__entities = dict()
        self.__entity_counter = 0
        self.executor = ThreadPoolExecutor()
        self.__cache = dict()

    def __getitem__(self, item):
        return self.__entities[item]

    @property
    def systems(self):
        """
        Returns:
            typing.Set[System]: set of systems contains in this world
        """
        return self.__systems

    @property
    def archetypes(self):
        """
        Returns:
            typing.Dict[type, typing.Set[int]]: dict of archetypes contains in this world
        """
        return self.__archetypes

    @property
    def entities(self):
        """
        Returns:
            typing.Dict[int, typing.Dict[type, object]]: dict of entities contains in this world
        """
        return self.__entities

    def system(self, func=None, /, *, family=None, parallel=True, **kwargs):
        """
        Register function as system. This can be used as a callable decorator with parameters or without a call.

        Examples:
            >>> world = World()
            >>>
            >>> @world.system
            >>> def foo(a: int):
            >>>     pass
            >>>
            >>>
            >>> @world.system(parallel=False, b=float)
            >>> def bar(b, c: list):
            >>>     pass
            >>>
            >>>
            >>> world.system(lambda var: pass, var=set)

        Args:
            func: function to be registered
            family: family label to bind systems. Default is None
            parallel (bool): if True, this system will be run in parallel. Default is True
            **kwargs: you can set which components this system will receive manually. Manual
                                               settings take priority over annotations and annotations will be updated
                                               to with settings dict (annotations.update(settings))

        Returns:

        """
        def wrap(fnc):
            return self.__register_system(fnc, family, parallel, **kwargs)

        if func is None:
            return wrap

        return wrap(func)

    def edit(self, entity) -> EntityBuilder:
        """
        Gives you EntityBuilder instance

        Args:
            entity: entity to edit

        Returns:
            EntityBuilder
        """
        entity = int(entity)
        if entity not in self.__entities:
            log.warning(f"entity <{entity}> not found in {self}")
        return EntityBuilder(self, entity)

    def reserve_id(self):
        """
        Inner method. Do not use it.
        """
        self.__entity_counter += 1
        return self.__entity_counter

    def spawn(self, *components: object) -> EntityBuilder:
        """
        Spawns the entity with given components and returns EntityBuilder

        Args:
            *components (object): instances of components

        Returns:
            EntityBuilder
        """
        return EntityBuilder.spawn(self, *components)

    def __register_system(self, system, family=None, parallel=True, **kwargs):
        query = dict(system.__annotations__)
        query.update(kwargs)
        query.pop('return', None)
        self.__systems.add(System(system, tuple(query.items()), family, parallel))
        log.debug(f'system `{system.__name__}` registered successfully')
        return system

    def associate_entity_with_archetype(self, entity: int, component: type):
        """
        Inner method. Do not use it.
        """
        self.register_component(component)
        self.__archetypes[component].add(entity)

    def register_component(self, component: type):
        if component not in self.__archetypes:
            self.__archetypes[component] = set()

    def request(self, with_components: tuple = None, without_components: tuple = None):
        if with_components is None:
            without_components = tuple()
        if without_components is None:
            without_components = tuple()

        if (with_components, without_components) in self.__cache:
            return self.__cache[(with_components, without_components)]
        entities = set(self.entities.keys())

        for name, component in with_components:
            entities.intersection_update(self.__archetypes[component])
        for name, component in without_components:
            entities.difference_update(self.__archetypes[component])

        # I would like to use generators instead of tuple,
        # but this leads to undefined behavior for a reason unknown to me
        response = {key: tuple(self.__entities[entity][value] for entity in entities) for key, value in with_components}
        response.update({key: (None,) * len(entities) for key, value in without_components})
        self.__cache[(with_components, without_components)] = response
        return response

    def call_family(self, family=None):
        """
        Starts the execution of family-related systems

        Args:
            family: family label. Default is None
        """
        tasks_no_par = []
        tasks_par = []
        # TODO: пределать параллелизм
        for system in (system for system in self.__systems if system.family == family):
            if system.parallel:
                tasks_par.append(self.executor.submit(system, **self.__prepare_query(system.query)))
            else:
                tasks_no_par.append((system, self.__prepare_query(system.query)))
        for system, kwargs in tasks_no_par:
            system(**kwargs)

    def __prepare_query(self, query):
        with_components = tuple((key, value) for key, value in query if not key.endswith("__"))
        without_components = tuple((key, value) for key, value in query if key.endswith("__"))
        return self.request(with_components, without_components)

    def shutdown(self, wait=True):
        """See ThreadPoolExecutor.shutdown"""
        self.executor.shutdown(wait)

    def clear_cache(self):
        self.__cache.clear()
