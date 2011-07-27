from tmapi.models import Topic

from base_manager import BaseManager
from name_element import NameElement
from name_part_type import NamePartType


class NamePartManager (BaseManager):

    def filter_by_name (self, name):
        association_type = self.eats_topic_map.name_has_name_part_association_type
        name_role_type = self.eats_topic_map.name_role_type
        name_part_role_type = self.eats_topic_map.name_part_role_type
        return self.filter(
            role_players__type=name_part_role_type,
            role_players__association__type=association_type,
            role_players__association__roles__type=name_role_type,
            role_players__association__roles__player=name)

    def get_query_set (self):
        return super(NamePartManager, self).get_query_set().filter(
            types=self.eats_topic_map.name_part_type)


class NamePart (Topic, NameElement):

    objects = NamePartManager()
    
    class Meta:
        proxy = True
        app_label = 'eats'

    def _get_name (self):
        """Returns the TMAPI `Name` associated with this name
        entity."""
        # QAZ: convert a possible IndexError into a more
        # useful/descriptive exception.
        return self.get_names()[0]

    @property
    def _language_role (self):
        """Returns the language role for this name.

        :rtype: `Role`

        """
        # QAZ: possible index errors.
        name_role = self.get_roles_played(
            self.eats_topic_map.name_part_role_type,
            self.eats_topic_map.is_in_language_type)[0]
        language_role = name_role.get_parent().get_roles(
            self.eats_topic_map.language_role_type)[0]
        return language_role
        
    @property
    def name_part_type (self):
        """Returns the name part type of this name.

        :rtype: `NamePartType`

        """
        return self._get_name().get_type(proxy=NamePartType)

    @name_part_type.setter
    def name_part_type (self, name_part_type):
        """Sets the name part type of this name part.

        :param name_part_type: type of name part
        :type name_type: `NamePartType`

        """
        self._get_name().set_type(name_part_type)

    def remove (self):
        for role in self.get_roles_played():
            association = role.get_parent()
            association.remove()
        super(NamePart, self).remove()
        
    @property
    def _script_role (self):
        """Returns the script role of this name.

        :rtype: `Role`

        """
        # QAZ: possible index errors.
        name_role = self.get_roles_played(
            self.eats_topic_map.name_part_role_type,
            self.eats_topic_map.is_in_script_type)[0]
        script_role = name_role.get_parent().get_roles(
            self.eats_topic_map.script_role_type)[0]
        return script_role
