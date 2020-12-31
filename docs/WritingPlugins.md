# Writing Plugins

The intention with the plugin system is to keep things as basic on boiler plate as possible. An interface
is provided for Plugins to subclass, which provides the reporting mechanism - the reporting mechanism may
change, expand, but the plugin architecture stays the same.

Plugins are updated in a thread, and are expected to complete within the update_interval. All plugins will
be started in sequence, likely based on their order in config.json, this may or may not be relevant to how
your plugin is executing but I wouldn't rely on the order being "correct" in the configuration file.

Changes which _are_ made to the plugin architecture will be made between major even release versions only.
Therefore the next API change wont be expected until 2.0, then 4.0 after that.

The basic plugin template looks like this
```python
from Malaria.Plugins import MalariaPlugin

class MyMalariaPlugin(MalariaPlugin):
    """
    A simple plugin to count the number of times it's called.
    """

    def __init__(self, malaria, **kwargs):
        super(MyMalariaPlugin, self).__init__(malaria, **kwargs)
        counter = 0

    def update(self):
        counter += 1
        self.report_reading('counter', counter)
```


For more complicated data sets you probably want to keep things simple and just dump a data structure
Malaria can take a data structure, flatten it to a topic and optionally only report the changed keys to
the MQTT service. Malaria will also allow use of _asdict and as_dict serialisation methods when performing
the flatten operation, arrays will be flattened as /x/ where x represents the index of the array object
and any multiple / errors are removed ensuring that empty keys and device paths are propertly serialised.

```python
def update(self):
    counter += 1
    self.report_data({
        'counter', counter
    })
```

You can specify a topic for your class to use by setting the topic at the class level, otherwise the class name
will be used.
```python
class MyMalariaPlugin(MalariaPlugin):
    __topic__ = "MyMalariaTopic/Data"
```

You can also specify patterns to ensure that a datapoint will be reported, even if it's unchanged. This uses
a regular expression parser, but be careful not to be over-zealous with complexity.
```python
__always_report__ = [
    'counter'
]
```

Adding configuration options to a plugin requires simply changing the class constructor.
```python
def __init__(self, malaria, initial_value=10, **kwargs):
    super(MyMalariaPlugin, self).__init__(malaria, **kwargs)
    counter = initial_value
```

The aim with these plugins is to do one thing really well and really fast, getting the data into some
structure where it can be made use of. Limited complexity, focused scope are the best kind of plugins.
If you feel you want to dump larger amounts of data, or larger structures it might be an idea to
break things down into multiple plugins where it makes sense to do so. Remember however, that sometimes
running the same process multiple times in multiple plugins will endure a cost.
