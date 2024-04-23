from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def check_topic_owner(request, topic):
    """To check the correct user is associated with the Topic."""
    # Make sure the Topic belongs to the current User
    if topic.owner != request.user:
        raise Http404   # Returning standard error
    
# Create your views here.
def index(request):
    """The home page for Learning Log."""
    return render(request, 'learning_logs/index.html')


def topics(request):
    """
    The page the view all the topics of the current user, 
    and all the public topics belonging to other users
    """
    # If the user is logged in need to show all the Topics including the owner Topics and Public Topics.
    if request.user.is_authenticated:
         
        topics = Topic.objects.filter(owner=request.user).order_by('date_added')
        # Wrapping the querry in parentheses allows to break up the querry in multiple lines. 
        public_topics = (Topic.objects.filter(public=True)
                         .exclude(owner=request.user)
                         .order_by('date_added'))
    # If the user is not authenticated can see the public querries. 
    else:
        topics = None
        public_topics = Topic.objects.filter(public=True).order_by('date_added')
        
    context = {'topics': topics, 'public_topics': public_topics}
    return render(request, 'learning_logs/topics.html', context)

def topic(request, topic_id):
    """Show a single topic and all its entries."""
    #topic = get_object_or_404(Topic, id=topic_id)
    # Make sure the Topic belongs to the current User
    #check_topic_owner(request, topic)
    
    # Get the topic corresponding with the Topic request. 
    topic = Topic.objects.get(id=topic_id)
    
    # Only want to make the owner to be able to edit or delete the Post
    is_owner = False
    if topic.owner == request.user:
        is_owner = True
    # If the topic belongs to someone else and is not public then show error page. 
    if topic.owner != request.user and not topic.public:
        raise Http404
    
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries, 'is_owner': is_owner}
    
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Add a new topic """
    if request.method != 'POST':
        # No data submitted, create a blank form. 
        form = TopicForm()
    else: 
        # POST data submitted, process data. 
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics') 
        
    # Display a blank or invalid form
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)
    # Check if the current user request is the same as the owner of the topic
    check_topic_owner(request, topic)
    
    if request.method != 'POST':
        # No data submitted creating blank form
        form = EntryForm()
    else:
        # POST data submitted, process data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            # Call the view function 'topic' so will see the entries. 
            return redirect('learning_logs:topic', topic_id=topic_id)
        
    # Display a blank or invalid form.
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    # Check if the correct user is logged in. 
    check_topic_owner(request, topic)
    
    if request.method != 'POST':
        # Initial request, pre-fill form with the current entry.       
        form = EntryForm(instance=entry)
    else: 
        # POST data submitted, process data 
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
        
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
    