from tmapi.models import Topic

from name_element import NameElement
from name_index import NameIndex
from name_part import NamePart
from name_type import NameType


class Name (Topic, NameElement):

    class Meta:
        proxy = True
        app_label = 'eats'

    def _add_name_index (self):
        """Adds the forms of this name to the name index."""
        parts = self.display_form.split()
        for part in parts:
            indexed_form = NameIndex(entity=self.entity, name=self, form=part)
            indexed_form.save()

    def create_name_part (self, name_part_type, language, script, display_form,
                          order):
        """Creates a name part associated with this name.

        :param name_part_type: type of the name part
        :type name_part_type: `NamePartType`
        :param language: language of the name part
        :type language: `Language` or None
        :param script: script of the name part
        :type script: `Script` or None
        :param display_form: form of the name part
        :type display_form: unicode string
        :param order: order of name part
        :type order: integer
        :rtype: `NamePart`

        """
        association_type = self.eats_topic_map.name_has_name_part_association_type
        name_role_type = self.eats_topic_map.name_role_type
        association = self.eats_topic_map.create_association(association_type)
        association.create_role(name_role_type, self)
        name_part = self.eats_topic_map.create_topic(proxy=NamePart)
        name_part.add_type(self.eats_topic_map.name_part_type)
        association.create_role(self.eats_topic_map.name_part_role_type,
                                name_part)
        name_part.create_name(display_form, name_part_type)
        language_association = self.eats_topic_map.create_association(
            self.eats_topic_map.is_in_language_type)
        language_association.create_role(
            self.eats_topic_map.name_part_role_type, name_part)
        language_association.create_role(self.eats_topic_map.language_role_type,
                                         language)
        name_part.create_occurrence(self.eats_topic_map.name_part_order_type,
                                    order)
        script_association = self.eats_topic_map.create_association(
            self.eats_topic_map.is_in_script_type)
        script_association.create_role(self.eats_topic_map.name_part_role_type,
                                       name_part)
        script_association.create_role(self.eats_topic_map.script_role_type,
                                       script)
        return name_part

    def _delete_name_index_forms (self):
        """Deletes the indexed forms of this name."""
        self.indexed_name_forms.all().delete()
        
    @property
    def entity (self):
        """Returns the entity to which this name belongs.

        :rtype: `Entity`
        
        """
        if not hasattr(self, '_entity'):
            from entity import Entity
            property_role = self.get_roles_played(
                self.eats_topic_map.property_role_type)[0]
            assertion = property_role.get_parent()
            entity_role = assertion.get_roles(
                self.eats_topic_map.entity_role_type)[0]
            self._entity = entity_role.get_player(proxy=Entity)
        return self._entity

    def get_name_parts (self):
        """Returns the name parts associated with this name.

        :rtype: `QuerySet` of `NamePart`s

        """
        return NamePart.objects.filter_by_name(self)
    
    @property
    def _language_role (self):
        """Returns the language role for this name.

        :rtype: `Role`

        """
        # QAZ: possible index errors.
        name_role = self.get_roles_played(
            self.eats_topic_map.name_role_type,
            self.eats_topic_map.is_in_language_type)[0]
        language_role = name_role.get_parent().get_roles(
            self.eats_topic_map.language_role_type)[0]
        return language_role
        
    @property
    def name_type (self):
        """Returns the name type of this name.

        :rtype: `NameType`

        """
        return self._get_name().get_type(proxy=NameType)

    @name_type.setter
    def name_type (self, name_type):
        """Sets the name type of this name.

        :param name_type: type of name
        :type name_type: `NameType`

        """
        self._get_name().set_type(name_type)
    
    def remove (self):
        for role in self.get_roles_played():
            association = role.get_parent()
            association.remove()
        super(Name, self).remove()
        
    @property
    def _script_role (self):
        """Returns the script role of this name.

        :rtype: `Role`

        """
        # QAZ: possible index errors.
        name_role = self.get_roles_played(
            self.eats_topic_map.name_role_type,
            self.eats_topic_map.is_in_script_type)[0]
        script_role = name_role.get_parent().get_roles(
            self.eats_topic_map.script_role_type)[0]
        return script_role

    def update (self, name_type, language, script, display_form):
        self.name_type = name_type
        self.language = language
        self.script = script
        self.display_form = display_form
        self.update_name_index()

    def update_name_index (self):
        """Updates the name index forms for this name."""
        self._delete_name_index_forms()
        self._add_name_index()
