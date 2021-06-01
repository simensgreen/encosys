#Encosys
Encosys (**en**tity **co**mponent **sys**tem) - implementation 
entity component system pattern _[link](https://en.wikipedia.org/wiki/Entity_component_system)_.
The main distinguishing feature of this implementation is the ability to use annotations 
in functions when declaring systems. But you better take an example!
####Example:
```python
from src import World, Entity
from dataclasses import dataclass, field


# Any object of any class can act as a component, be it an int or your own class
@dataclass
class MyComponent1:
    x: float
    y: float


@dataclass
class MyComponent2:
    data: dict = field(default_factory=dict)


# World - container and dispatcher of all entities, systems and components
world = World()


# disable parallel execution, for example
@world.system(parallel=False)
def foo(first: MyComponent1):
    """
    This system will receive component
    instances of only those entities
    that have a component MyComponent1
    """
    for component in iter(first):
        print(component)


# it is still possible to define the query manually or using annotation
@world.system(first=MyComponent1, second=MyComponent2)
def bar(first, second, entities: Entity):
    """
    This system will receive component
    instances of only those entities 
    that have both MyComponent1 and MyComponent2
    """
    for f, s, e in zip(first, second, entities):
        print(f"first: {f}, second: {s}, entity id: {e}")


# simple definition
@world.system
def fizz(entities: Entity, _first: MyComponent1, _second__: MyComponent2):
    """
    This system will receive component 
    instances of only those entities 
    that have MyComponent1, but do not have MyComponent2
    """
    for entity in iter(entities):
        print(f"entity {entity} have {MyComponent1} and have not {MyComponent2}")


# spawn some entities
world.spawn(MyComponent1(1, 1), MyComponent2({"foo": "bar"}))
world.spawn(MyComponent1(2, 2))
world.spawn(MyComponent2({"fizz": "bazz"}))
world.spawn(MyComponent1(3, 3), MyComponent2({"foo": "bar"}))

# call all defined systems once
world.call_family()
world.shutdown()

```