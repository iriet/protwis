from django.shortcuts import render
from django.views import generic

from common.classes import SimpleSelection
from common.classes import Selection
from common.classes import SelectionItem
from protein.models import Protein
from protein.models import ProteinFamily

import inspect


class AbsTargetSelection(generic.TemplateView):
    """An abstract class for the target selection page used in many apps. To use it in another app, create a class 
    based view for that app that extends this class"""
    template_name = 'common/targetselection.html'

    step = 1
    number_of_steps = 2
    title = 'Select targets'
    description = 'Select receptors by searching or browsing in the middle column. You can select entire receptor families or individual receptors.\n\nSelected receptors will appear in the right column, where you can edit the list.\n\nOnce you have selected all your receptors, click the green button.'
    docs = '/docs/protein'
    pfs = ProteinFamily.objects.all()
    ps = Protein.objects.all()

    def get_context_data(self, **kwargs):
        """get context from parent class (really only relevant for child classes of this class, as TemplateView does
        not have any context variables)"""
        context = super().get_context_data(**kwargs)

        # get attributes of this class and add them to the context
        attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
        for a in attributes:
            if not(a[0].startswith('__') and a[0].endswith('__')):
                context[a[0]] = a[1]
        return context


def AddToSelection(request):
    """Receives a selection request, adds the selected item to session, and returns the current selection"""
    selection_type = request.GET['selection_type']
    selection_subtype = request.GET['selection_subtype']
    selection_id = request.GET['selection_id']
    
    if selection_subtype == 'protein':
        p = Protein.objects.get(entry_name=selection_id)
        selection_object = SelectionItem('protein', p)
    elif selection_subtype == 'family':
        pf = ProteinFamily.objects.get(slug=selection_id)
        selection_object = SelectionItem('family', pf)
    elif selection_subtype == 'set':
        ps = ProteinSet.objects.get(pk=selection_id)
        selection_object = SelectionItem('set', ps)

    # get simple selection from session
    simple_selection = request.session.get('selection', False)
    
    # create full selection and import simple selection (if it exists)
    selection = Selection()
    if simple_selection:
        selection.importer(simple_selection)

    # add the selected item to the selection
    sel_type = getattr(selection, selection_type)
    selection.add(selection_type, selection_subtype, selection_object)

    # export simple selection that can be serialized
    simple_selection = selection.exporter()

    # add simple selection to session
    request.session['selection'] = simple_selection
    
    return render(request, 'common/selection.html', selection.render())

def ClearSelection(request):
    # create a blank selection
    selection = Selection()

    # export simple selection that can be serialized
    simple_selection = selection.exporter()

    # add simple selection to session
    request.session['selection'] = simple_selection
    
    return render(request, 'common/selection.html', selection.render())