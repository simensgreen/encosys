import pytest
from __init__ import World, Entity
from dataclasses import dataclass, field


@pytest.fixture()
def world():
    return World()


@pytest.fixture()
def components():
    @dataclass
    class Component1:
        x: float = field(default=0)
        y: float = field(default=0)

    @dataclass
    class Component2:
        o: dict = field(default_factory=dict)

    class Component3:
        pass

    return [Component1, Component2, Component3]


def test_empty_world(world):
    assert world.entities == dict()
    assert world.systems == set()
    assert world.archetypes == dict()


def test_spawn_entity(world):
    entity = world.spawn().id
    assert entity in world.entities


def test_insert_components(world, components):
    entity = world.spawn(components[0](0, 0)).insert(components[2]()).id
    assert world.archetypes == {components[0]: {entity}, components[2]: {entity}, Entity: {entity}}


def test_system_insertion(world, components):
    def system_1(a: components[1]):
        for a_ in a:
            assert isinstance(a_, components[1])

    world.system(system_1, parallel=False)
    world.spawn(components[1]())
    world.call_family()


def test_system_decorator(world, components):

    @world.system(parallel=False)
    def system_1(a: components[2]):
        for a_ in a:
            assert isinstance(a_, components[2])

    world.spawn(components[2]())
    world.call_family()
