from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from tmapi.indices import TypeInstanceIndex
from tmapi.models import Locator, Topic, TopicMap

from eats.constants import ADMIN_NAME_TYPE_IRI, AUTHORITY_TYPE_IRI, ENTITY_ROLE_TYPE_IRI, ENTITY_TYPE_IRI, ENTITY_TYPE_ASSERTION_TYPE_IRI, ENTITY_TYPE_TYPE_IRI, EXISTENCE_ASSERTION_TYPE_IRI, LANGUAGE_CODE_TYPE_IRI, LANGUAGE_TYPE_IRI, PROPERTY_ROLE_TYPE_IRI, SCRIPT_CODE_TYPE_IRI, SCRIPT_TYPE_IRI
from entity import Entity

class EATSTopicMap (TopicMap):

    code_type_iris = {
        LANGUAGE_TYPE_IRI: LANGUAGE_CODE_TYPE_IRI,
        SCRIPT_TYPE_IRI: SCRIPT_CODE_TYPE_IRI,
        }
    
    class Meta:
        proxy = True

    @property
    def admin_name_type (self):
        self._admin_name_type = getattr(self, '_admin_name_type', None)
        if self._admin_name_type is None:
            self._admin_name_type = self.create_topic_by_subject_identifier(
                Locator(ADMIN_NAME_TYPE_IRI))
        return self._admin_name_type

    def convert_topic_to_entity (self, topic):
        """Returns `topic` as an instance of `Entity`.

        :param topic: the `Topic` representing the entity
        :type topic: `Topic`
        :rtype: `Entity`

        """
        entity = Entity.objects.get(pk=topic.id)
        entity.eats_topic_map = self
        return entity
        
    def create_entity (self, authority):
        """Creates a new entity, using `authority` to create an
        accompanying existence property assertion.

        :param authority: authority used in the existence property assertion
        :type authority: `Topic`
        :rtype: `Entity`

        """
        topic = self.create_topic()
        entity = self.convert_topic_to_entity(topic)
        view_url = reverse('entity-view', kwargs={'entity_id': entity.id})
        url = 'http://%s/%s' % (Site.objects.get_current().domain, view_url)
        entity.add_subject_identifier(Locator(url))
        entity.add_type(self.entity_type)
        entity.create_existence_property_assertion(authority)
        return entity

    def create_typed_topic (self, type_iri, data=None):
        """Creates a topic of the specified type.

        :param type_iri: IRI used as the Subject Identifier for the
          typing topic
        :type type_iri: string
        :param data: optional data to be saved with the topic to be created
        :type name: dictionary or None
        :rtype: `Topic`

        """
        # QAZ: The data part of this method is very admin specific,
        # and should perhaps be refactored.
        topic = self.create_topic()
        topic_type = self.create_topic_by_subject_identifier(
            Locator(type_iri))
        print self.id
        print topic_type.topic_map.id
        topic.add_type(topic_type)
        if data is not None:
            # Different data to save depending on the type.
            topic.create_name(data['name'], name_type=self.admin_name_type)
            if 'code' in data:
                if type_iri == LANGUAGE_TYPE_IRI:
                    occurrence_type_iri = LANGUAGE_CODE_TYPE_IRI
                elif type_iri == SCRIPT_TYPE_IRI:
                    occurrence_type_iri = SCRIPT_CODE_TYPE_IRI
                occurrence_type = self.create_topic_by_subject_identifier(
                    Locator(occurrence_type_iri))
                topic.create_occurrence(occurrence_type, data.get('code'))
        return topic

    @property
    def entity_role_type (self):
        self._entity_role_type = getattr(self, '_entity_role_type', None)
        if self._entity_role_type is None:
            self._entity_role_type = self.get_topic_by_subject_identifier(
                Locator(ENTITY_ROLE_TYPE_IRI))
        return self._entity_role_type

    @property
    def entity_type_assertion_type (self):
        self._entity_type_assertion_type = getattr(
            self, '_entity_type_assertion_type', None)
        if self._entity_type_assertion_type is None:
            self._entity_type_assertion_type = self.get_topic_by_subject_identifier(Locator(ENTITY_TYPE_ASSERTION_TYPE_IRI))
        return self._entity_type_assertion_type
    
    @property
    def entity_type (self):
        self._entity_type = getattr(self, '_entity_type', None)
        if self._entity_type is None:
            self._entity_type = self.create_topic_by_subject_identifier(
                Locator(ENTITY_TYPE_IRI))
        return self._entity_type

    @property
    def entity_types (self):
        """Returns a `QuerySet` of entity type `Topic`s.

        :rtype: `QuerySet` of `Topic`s

        """
        return self.get_topics_by_type(ENTITY_TYPE_TYPE_IRI)

    @property
    def existence_assertion_type (self):
        self._existence_assertion_type = getattr(
            self, '_existence_assertion_type', None)
        if self._existence_assertion_type is None:
            self._existence_assertion_type = self.get_topic_by_subject_identifier(Locator(EXISTENCE_ASSERTION_TYPE_IRI))
        return self._existence_assertion_type
    
    def get_admin_name (self, topic):
        """Returns the administrative name of `topic`.

        :param topic: the topic whose administrative name is to be returned
        :type topic: `Topic`
        :rtype: `Name`

        """
        # There should only be a single such name, but this is not
        # enforced at the TMAPI level. There seems little need to raise an
        # error here if there is more than one.
        return topic.get_names(self.admin_name_type)[0]
    
    def get_authorities (self):
        """Returns the authorities in this topic map.

        :rtype: `QuerySet` of `Topic`s

        """
        return self.get_topics_by_type(AUTHORITY_TYPE_IRI)

    def get_entity (self, entity_id):
        """Returns the entity with identifier `entity_id`.

        :param entity_id: the entity's identifier
        :type entity_id: string
        :rtype: `Entity`

        """
        topic = self.get_construct_by_id(entity_id)
        return self.convert_topic_to_entity(topic)

    def get_topic_by_id (self, topic_id, type_iri):
        """Returns the topic with `topic_id`, or None if there is no
        such topic that is of the type specified by `type_iri`.

        :param topic_id: identifier of the topic
        :type topic_id: integer
        :param type_iri: IRI used as the Subject Identifier for the
          typing topic
        :type type_iri: string
        :rtype: `Topic`

        """
        topic = self.get_construct_by_id(topic_id)
        if topic is not None:
            topic_type = self.get_topic_by_subject_identifier(
                Locator(type_iri))
            if not isinstance(topic, Topic) or \
                    topic_type not in topic.types.all():
                topic = None
        return topic

    def get_topic_data (self, topic, type_iri):
        """Returns the data associated with topic.

        :param topic: the topic whose data is to be retrieved
        :type topic: `Topic`
        :param type_iri: IRI used as the SubjectIdentifier for the typing topic
        :type type_iri: string

        """
        # QAZ: This is very specific to admin functionality, and
        # should perhaps be renamed.
        data = {}
        data['name'] = self.get_admin_name(topic)
        if type_iri in (LANGUAGE_TYPE_IRI, SCRIPT_TYPE_IRI):
            code_type_iri = self.code_type_iris[type_iri]
            code_occurrence_type = self.get_topic_by_subject_identifier(
                Locator(code_type_iri))
            code_occurrence = topic.get_occurrences(code_occurrence_type)[0]
            data['code'] = code_occurrence.get_value()
        return data
    
    def get_topics_by_type (self, type_iri):
        """Returns a `QuerySet` of `Topic`s of the the type specified
        by `type_iri`.

        :param type_iri: IRI used as the Subject Identifier for the
          typing topic
        :type type_iri: string
        :rtype: `QuerySet` of `Topic`s

        """
        topic_type = self.create_topic_by_subject_identifier(
            Locator(type_iri))
        index = self.get_index(TypeInstanceIndex)
        index.open()
        return index.get_topics(topic_type)
        
    @property
    def property_role_type (self):
        self._property_role_type = getattr(self, '_property_role_type',
                                           None)
        if self._property_role_type is None:
            self._property_role_type = self.get_topic_by_subject_identifier(
                Locator(PROPERTY_ROLE_TYPE_IRI))
        return self._property_role_type
    
    def topic_exists (self, type_iri, name, topic_id):
        """Returns True if this topic map contains a topic with the
        type specified by `type_iri` and whose administrative name is
        `name`.

        If `topic_id` is not None, return False if the matching topic
        has that id, to allow for a topic to be excluded from the check.

        :param type_iri: IRI used as the Subject Identifier for the
          typing topic
        :type type_iri: string
        :param name: administrative name of the topic
        :type name: string
        :param topic_id: id of a topic to be ignored when testing
        :type topic_id: integer
        :rtype: Boolean

        """
        if topic_id is not None:
            topic = self.get_topic_by_id(topic_id, type_iri)
            if name == self.get_admin_name(topic).get_value():
                return False
        topics = self.get_topics_by_type(type_iri)
        for topic in topics:
            if name == self.get_admin_name(topic).get_value():
                return True
        return False

    def update_topic_by_type (self, topic, type_iri, data):
        """Updates `topic` with the information in `data`.

        :param topic: the topic to be updated
        :type topic: `Topic`
        :param type_iri: IRI used as the SubjectIdentifier for the typing topic
        :type type_iri: string

        """
        # QAZ: This is very specific to admin functionality, and
        # should perhaps be renamed.
        self.get_admin_name(topic).set_value(data.get('name'))
        if type_iri in (LANGUAGE_TYPE_IRI, SCRIPT_TYPE_IRI):
            code_type_iri = self.code_type_iris[type_iri]
            code_occurrence_type = self.get_topic_by_subject_identifier(
                Locator(code_type_iri))
            # QAZ: assuming that there is a single such occurrence, or
            # that the others are not useful.
            code_occurrence = topic.get_occurrences(code_occurrence_type)[0]
            code_occurrence.set_value(data.get('code'))
