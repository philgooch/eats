import StringIO

from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from lxml import etree

from eats.lib.eatsml_exporter import EATSMLExporter
from eats.lib.eatsml_importer import EATSMLImporter
from eats.lib.property_assertions import EntityRelationshipPropertyAssertions, EntityTypePropertyAssertions, ExistencePropertyAssertions, NamePropertyAssertions, NotePropertyAssertions, SubjectIdentifierPropertyAssertions
from eats.lib.user import get_user_preferences, user_is_editor
from eats.lib.views import get_topic_or_404
from eats.decorators import add_topic_map
from eats.forms.edit import CreateEntityForm, create_choice_list, CurrentAuthorityForm, DateForm, EATSMLImportForm
from eats.models import Authority, Calendar, DatePeriod, DateType, EATSMLImport, Entity


@user_passes_test(user_is_editor)
@add_topic_map
def entity_add (request, topic_map):
    editor = request.user.eats_user
    authorities = editor.editable_authorities.all()
    if request.method == 'POST':
        form = CreateEntityForm(topic_map, authorities, request.POST)
        if form.is_valid():
            authority_id = form.cleaned_data['authority']
            authority = Authority.objects.get_by_identifier(authority_id)
            if authority != editor.get_current_authority():
                editor.set_current_authority(authority)
            entity = topic_map.create_entity(authority)
            redirect_url = reverse('entity-change',
                                   kwargs={'entity_id': entity.get_id()})
            return HttpResponseRedirect(redirect_url)
    else:
        form = CreateEntityForm(topic_map, authorities)
    context_data = {'form': form}
    return render_to_response('eats/edit/entity_add.html', context_data,
                              context_instance=RequestContext(request))

@user_passes_test(user_is_editor)
@add_topic_map
def entity_change (request, topic_map, entity_id):
    entity = get_topic_or_404(Entity, entity_id)
    editor = request.user.eats_user
    context_data = {'entity': entity}
    authority = editor.get_current_authority()
    editable_authorities = editor.editable_authorities.all()
    authority_data = {'current_authority': authority.get_id()}
    entity_data = None
    if request.method == 'POST':
        if '_change_authority' in request.POST:
            authority_data = request.POST
        else:
            entity_data = request.POST
    current_authority_form = CurrentAuthorityForm(
        topic_map, editable_authorities, authority_data)
    existences = ExistencePropertyAssertions(topic_map, entity, authority,
                                             entity_data)
    entity_types = EntityTypePropertyAssertions(topic_map, entity, authority,
                                                entity_data)
    names = NamePropertyAssertions(topic_map, entity, authority, entity_data)
    notes = NotePropertyAssertions(topic_map, entity, authority, entity_data)
    entity_relationships = EntityRelationshipPropertyAssertions(
        topic_map, entity, authority, entity_data)
    subject_identifiers = SubjectIdentifierPropertyAssertions(
        topic_map, entity, authority, entity_data)
    existences_formset = existences.formset
    entity_types_formset = entity_types.formset
    names_formset = names.formset
    notes_formset = notes.formset
    entity_relationships_formset = entity_relationships.formset
    subject_identifiers_formset = subject_identifiers.formset
    if request.method == 'POST':
        redirect_url = reverse('entity-change', kwargs={'entity_id': entity_id})
        if '_change_authority' in request.POST:
            if current_authority_form.is_valid():
                authority_id = current_authority_form.cleaned_data[
                    'current_authority']
                authority = Authority.objects.get_by_identifier(authority_id)
                editor.set_current_authority(authority)
                return HttpResponseRedirect(redirect_url)
        else:
            formsets = (existences_formset, entity_types_formset,
                        names_formset, notes_formset,
                        entity_relationships_formset,
                        subject_identifiers_formset)
            is_valid = False
            for formset in formsets:
                is_valid = formset.is_valid()
                if not is_valid:
                    break
            if is_valid:
                for formset in formsets:
                    formset.save()
                return HttpResponseRedirect(redirect_url)
    context_data['current_authority_form'] = current_authority_form
    context_data['existence_non_editable'] = existences.non_editable
    context_data['existence_formset'] = existences_formset
    context_data['entity_type_non_editable'] = entity_types.non_editable
    context_data['entity_type_formset'] = entity_types_formset
    context_data['name_non_editable'] = names.non_editable
    context_data['name_formset'] = names_formset
    context_data['note_formset'] = notes_formset
    context_data['note_non_editable'] = notes.non_editable
    context_data['entity_relationship_formset'] = entity_relationships_formset
    context_data['entity_relationship_non_editable'] = entity_relationships.non_editable
    context_data['subject_identifier_formset'] = subject_identifiers_formset
    context_data['subject_identifier_non_editable'] = subject_identifiers.non_editable
    user_preferences = get_user_preferences(request)
    context_data.update(user_preferences)
    preferred_name_assertion = entity.get_preferred_name(
        user_preferences['preferred_authority'],
        user_preferences['preferred_language'],
        user_preferences['preferred_script'])
    if preferred_name_assertion:
        context_data['preferred_name'] = preferred_name_assertion.name.assembled_form
    else:
        context_data['preferred_name'] = '[unnamed entity]'
    return render_to_response('eats/edit/entity_change.html', context_data,
                              context_instance=RequestContext(request))

@user_passes_test(user_is_editor)
@add_topic_map
def entity_delete (request, topic_map, entity_id):
    entity = get_topic_or_404(Entity, entity_id)
    editable_authorities = request.user.eats_user.editable_authorities.all()
    assertion_getters = [entity.get_eats_names, entity.get_entity_relationships,
                         entity.get_entity_types, entity.get_existences,
                         entity.get_subject_identifiers, entity.get_notes]
    can_delete = True
    for assertion_getter in assertion_getters:
        for assertion in assertion_getter():
            if assertion.authority not in editable_authorities:
                can_delete = False
    if request.method == 'POST' and can_delete:
        entity.remove()
        return HttpResponseRedirect(reverse('search'))
    context_data = {'can_delete': can_delete}
    return render_to_response('eats/edit/entity_delete.html', context_data,
                              context_instance=RequestContext(request))

@user_passes_test(user_is_editor)
@add_topic_map
def date_add (request, topic_map, entity_id, assertion_id):
    entity = get_topic_or_404(Entity, entity_id)
    assertion = entity.get_assertion(assertion_id)
    if assertion is None:
        raise Http404
    authority = assertion.authority
    if authority != request.user.eats_user.get_current_authority():
        raise Http404
    calendar_choices = create_choice_list(
        topic_map, Calendar.objects.filter_by_authority(authority))
    date_period_choices = create_choice_list(
        topic_map, DatePeriod.objects.filter_by_authority(authority))
    date_type_choices = create_choice_list(
        topic_map, DateType.objects.filter_by_authority(authority))
    if request.method == 'POST':
        form = DateForm(topic_map, calendar_choices, date_period_choices,
                        date_type_choices, request.POST)
        if form.is_valid():
            date_id = form.save(assertion)
            if '_continue' in form.data:
                redirect_ids = {'assertion_id': assertion_id,
                                'date_id': date_id, 'entity_id': entity_id}
                redirect_url = reverse('date-change', kwargs=redirect_ids)
            else:
                redirect_ids = {'entity_id': entity_id}
                redirect_url = reverse('entity-change', kwargs=redirect_ids)
            return HttpResponseRedirect(redirect_url)
    else:
        form = DateForm(topic_map, calendar_choices, date_period_choices,
                        date_type_choices)
    context_data = {'form': form}
    return render_to_response('eats/edit/date_add.html', context_data,
                              context_instance=RequestContext(request))

@user_passes_test(user_is_editor)
@add_topic_map
def date_change (request, topic_map, entity_id, assertion_id, date_id):
    entity = get_topic_or_404(Entity, entity_id)
    assertion = entity.get_assertion(assertion_id)
    if assertion is None:
        raise Http404
    date = assertion.get_date(date_id)
    if date is None:
        raise Http404
    authority = assertion.authority
    if authority != request.user.eats_user.get_current_authority():
        raise Http404
    calendar_choices = create_choice_list(
        topic_map, Calendar.objects.filter_by_authority(authority))
    date_period_choices = create_choice_list(
        topic_map, DatePeriod.objects.filter_by_authority(authority))
    date_type_choices = create_choice_list(
        topic_map, DateType.objects.filter_by_authority(authority))
    if request.method == 'POST':
        form = DateForm(topic_map, calendar_choices, date_period_choices,
                        date_type_choices, request.POST, instance=date)
        redirect_ids = {'entity_id': entity_id}
        redirect_url = reverse('entity-change', kwargs=redirect_ids)
        if '_delete' in form.data:
            form.delete()
            return HttpResponseRedirect(redirect_url)
        if form.is_valid():
            date_id = form.save()
            if '_continue' in form.data:
                redirect_ids['assertion_id'] = assertion_id
                redirect_ids['date_id'] = date_id
                redirect_url = reverse('date-change', kwargs=redirect_ids)
            return HttpResponseRedirect(redirect_url)
    else:
        form = DateForm(topic_map, calendar_choices, date_period_choices,
                        date_type_choices, instance=date)
    context_data = {'form': form}
    return render_to_response('eats/edit/date_change.html', context_data,
                              context_instance=RequestContext(request))

@user_passes_test(user_is_editor)
@add_topic_map
def export_eatsml_base (request, topic_map):
    tree = EATSMLExporter(topic_map).export_infrastructure(
        user=request.user.eats_user)
    xml = etree.tostring(tree, encoding='utf-8', pretty_print=True)
    return HttpResponse(xml, mimetype='text/xml')

@user_passes_test(user_is_editor)
@add_topic_map
def export_eatsml_entities (request, topic_map):
    """Exports all entities in EATSML."""
    entities = Entity.objects.all()
    tree = EATSMLExporter(topic_map).export_entities(entities)
    xml = etree.tostring(tree, encoding='utf-8', pretty_print=True)
    return HttpResponse(xml, mimetype='text/xml')

@user_passes_test(user_is_editor)
@add_topic_map
def export_eatsml_full (request, topic_map):
    """Exports all EATS data in EATSML."""
    tree = EATSMLExporter(topic_map).export_full()
    xml = etree.tostring(tree, encoding='utf-8', pretty_print=True)
    return HttpResponse(xml, mimetype='text/xml')

@user_passes_test(user_is_editor)
@add_topic_map
def import_eatsml (request, topic_map):
    """Imports a POSTed EATSML file."""
    if request.method == 'POST':
        form = EATSMLImportForm(request.POST, request.FILES)
        user = request.user.eats_user
        if form.is_valid():
            eatsml_file = StringIO.StringIO()
            for chunk in request.FILES['import_file'].chunks():
                eatsml_file.write(chunk)
            eatsml_file.seek(0)
            # QAZ: After dealing with the uploaded file in chunks
            # above, to prevent overwhelming the system with a huge
            # file, straightaway the whole value is retrieved and
            # passed to the importer.
            eatsml = eatsml_file.getvalue()
            with transaction.commit_manually():
                try:
                    import_tree, annotated_tree = EATSMLImporter(
                        topic_map).import_xml(eatsml, user)
                    transaction.commit()
                except Exception, e:
                    transaction.rollback()
                    response = render_to_response(
                        '500.html', {'message': e},
                        context_instance=RequestContext(request))
                    response.status_code = 500
                    return response
            description = form.cleaned_data['description']
            imported_xml = etree.tostring(import_tree, encoding='utf-8',
                                          pretty_print=True)
            annotated_xml = etree.tostring(annotated_tree, encoding='utf-8',
                                           pretty_print=True)
            eatsml_import = EATSMLImport(
                importer=user, description=description, raw_xml=imported_xml,
                annotated_xml=annotated_xml)
            eatsml_import.save()
            redirect_url = reverse('display-eatsml-import',
                                   kwargs={'import_id': eatsml_import.id})
            return HttpResponseRedirect(redirect_url)
    else:
        form = EATSMLImportForm()
    import_list = EATSMLImport.objects.values('id', 'importer__user__username',
                                              'description', 'import_date')
    paginator = Paginator(import_list, 100)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        imports = paginator.page(page)
    except (EmptyPage, InvalidPage):
        imports = paginator.page(paginator.num_pages)
    context_data = {'form': form, 'imports': imports}
    return render_to_response('eats/edit/eatsml_import.html', context_data,
                              context_instance=RequestContext(request))

@user_passes_test(user_is_editor)
def display_eatsml_import (request, import_id):
    eatsml_import = get_object_or_404(EATSMLImport, pk=import_id)
    context_data = {'import': eatsml_import}
    return render_to_response(
        'eats/edit/eatsml_import_display.html', context_data,
        context_instance=RequestContext(request))

@user_passes_test(user_is_editor)
def display_eatsml_import_raw (request, import_id):
    eatsml_import = get_object_or_404(EATSMLImport, pk=import_id)
    return HttpResponse(eatsml_import.raw_xml, mimetype='text/xml')

@user_passes_test(user_is_editor)
def display_eatsml_import_annotated (request, import_id):
    eatsml_import = get_object_or_404(EATSMLImport, pk=import_id)
    return HttpResponse(eatsml_import.annotated_xml, mimetype='text/xml')
