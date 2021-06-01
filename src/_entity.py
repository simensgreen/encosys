import logging

log = logging.getLogger(__name__)


class Entity(int):
    pass


class EntityBuilder:
    """
    Objects of this class help to create, delete, edit entities
    """
    def __init__(self, world, entity):
        self.__world = world
        self.__id = entity

    def insert(self, *components: object):
        """
        Inserts components to entity.
        Duplicated components is not allowed.
        Manual addition of entity component is not allowed.

        Args:
            *components (object): instances of components

        Returns:
            EntityBuilder: self
        """
        entity_data = {}
        for component in components:
            comp_class = component.__class__
            self.__world.associate_entity_with_archetype(self.__id, comp_class)
            entity_data[comp_class] = component
        self.__world.entities[self.__id].update(entity_data)
        self.__world.clear_cache()
        return self

    def remove(self, *components: type):
        """
        Removes components from entity
        Args:
            *components (type): types of components
        """
        for component in components:
            self.__world.archetypes[component].remove(self.__id)
            self.__world.entities[self.__id].pop(component, None)
        self.__world.clear_cache()

    def despawn(self):
        """
        Removes entity from world
        """
        for component in self.__world.entities.pop(self.__id, ()):
            self.__world.archetypes[component].remove(self.__id)
        self.__world.clear_cache()

    @property
    def id(self):
        """
        Returns:
            id of current entity
        """
        return self.__id

    @staticmethod
    def spawn(world, *components: object):
        """
        Spawns the entity with given components and returns EntityBuilder

        Args:
            world (World): the world in which the entity will be created
            *components (object): instances of components

        Returns:
            EntityBuilder
        """
        entity = world.reserve_id()
        if any(isinstance(comp, Entity) for comp in components):
            log.critical(f'found explicitly Entity component: {components}')
            raise AttributeError(f"explicitly Entity component in {components}")
        components += (Entity(entity),)
        world.entities[entity] = dict()
        return EntityBuilder(world, entity).insert(*components)
