# Malaria Architecture

Malaria is designed to be *as simple as possible* there are no complex bells and whistles added to
it which make debugging hard or invite complexity over time.

Malaria is built around a plugin loader which simply iterates the modules in the plugin path, collecting
the available classes which subclass MalariaPlugin, these subclasses can be activated or deactivated by
providing their configuration as a minimum "enabled" in the config.json file.

Plugins are updated in their own threads, which in turn call back to the Malaria class, which then queues
the topics and values for publication to the mosquitto server.

Most of this code is found in ```__init__.py```, the interface which plugins use is found in ```Plugins/__init__.py```
and there you'll also find a bunch of example plugins which more-or-less cover the majority of cases.

 - [Home](../)
 - [Writing Plugins](WritingPlugins.md)
 - [License](License.md)
