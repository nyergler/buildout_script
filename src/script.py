"""zc.buildout recipe to create a simple script with details filled in
(potentially) from the buildout.cfg."""

import os
import stat
import logging

import zc.buildout
import pkg_resources

class Script:

    def __init__(self, buildout, name, options):

        self.buildout = buildout
        self.name = name
        self.options = options

        self._template_name = self.options.get('template', None)
        self._target_name = self.options.get('target', None)

        # make sure the template was specified
        if self._template_name is None:
            logging.getLogger(self.name).error("Missing template parameter")
            raise zc.buildout.UserError("A template must be specified.")

        # see if the target was specified
        if self._target_name is None:

            # none specified, use the default name
            # (the template with the extension split off
            self._target_name = self._template_name.rsplit('.', 1)[0]

        # make sure the template exists
        self._get_template(self._template_name)

    def _get_template(self, template_name):
        """Given a template name, attempt to resolve it and return the
        contents as a String."""

        if pkg_resources.resource_exists(__name__, 'templates/%s'
                                         % template_name):

            # loading from our recipe egg
            return pkg_resources.resource_string(__name__, 'templates/%s'
                                                 % template_name)

        else:
            # see if the user specified a templates directory
            template_dir = self.options.get('template_dir',
               os.path.join(self.buildout['buildout']['directory'],
                            'templates'))
            
            if os.path.exists(os.path.join(template_dir, template_name)):
                return file(os.path.join(template_dir, template_name)).read()

        # unable to find template, throw an error
        logging.getLogger(self.name).error("Template %s does not exist." %
                                           template_name)
        raise zc.buildout.UserError(
            "The specified template, %s, does not exist" % template_name)
        
    def install(self):
        """Duplicate the template script as the specified target, applying
        Python string formatting first.  The dictionary passed to string
        formatting is a flattened dictionary of buildout options and
        the part options."""

        script_template = self._get_template(self._template_name)

        info_dict = self.buildout['buildout'].copy()
        info_dict.update(self.options)
        info_dict.update({'part-name':self.name})

        # write the new script out
        script_fn = os.path.join(self.buildout['buildout']['bin-directory'],
                                 self._target_name)
        file(script_fn, 'w').write(script_template % info_dict)

        # set the permissions to allow execution
        os.chmod(script_fn, os.stat(script_fn).st_mode|
                 stat.S_IXOTH|stat.S_IXGRP|stat.S_IXUSR)
        
        return [script_fn]

    update = install
    
