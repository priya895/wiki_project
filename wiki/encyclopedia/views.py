from django.urls import reverse
from django.shortcuts import render
from django import forms
from . import util
import markdown
import secrets
from django.http.response import HttpResponseRedirect


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request,entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonExist.html",{
            "entryTitle":entry
        })
    else:
        return render(request,"encyclopedia/entry.html",{
            "entry":markdown.markdown(entryPage),
            "entryTitle":entry
        })
def search(request):
    result=request.GET.get('q','')
    if(util.get_entry(result) is not None):
        return HttpResponseRedirect(reverse("entry",kwargs={'entry':result}))
    else:
        sub=[]
        for entry in util.list_entries():
            if result.upper() in entry.upper():
                sub.append(entry)
        return render(request,"encyclopedia/index.html",{
        "entries":sub,
        "search":True,
        "value":result
    })
def random(request):
    entry=util.list_entries()
    randomentry=secrets.choice(entry)
    return HttpResponseRedirect(reverse("entry",kwargs={'entry':randomentry}))
class newentry(forms.Form):
    title=forms.CharField(label="Entry Title",widget=forms.TextInput(attrs={'placeholder': 'enter the title','style':'margin-left:25px'}))
    newentry=forms.CharField(label="Entry Content",widget=forms.Textarea(attrs={'palceholder':'enter some content','rows':3,"cols":20,'style':'vertical-align:top'}))
    edit=forms.BooleanField(initial=False,widget=forms.HiddenInput(),required=False)
def newpage(request):
    if request.method=="POST":
        form=newentry(request.POST)
        if form.is_valid():
            title=form.cleaned_data["title"]
            content=form.cleaned_data["newentry"]
            if util.get_entry(title) is None or form.cleaned_data["edit"] is True:
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry",kwargs={'entry':title}))
            else:
                return render(request,"encyclopedia/newpage.html",{
                    "form":form,
                    "exists": True,
                    "entrytitle":title
                })
        else:
            return render(request,"encyclopedia/newpage.html",{
                "form":form,
                "exists":False
            })
    else:
        return render(request,"encyclopedia/newpage.html",{
            "form":newentry(),
            "exists":False
        })
def edit(request,entry):
    page=util.get_entry(entry)
    if page is None:
        return render(request,"encyclopedia/nonExist.html",{
            "entrytitle":entry
        })
    else:
        form = newentry()
        form.fields["title"].initial=entry
        form.fields["title"].widget=forms.HiddenInput()
        form.fields["newentry"].initial=page
        form.fields["edit"].initial=True
        return render(request,"encyclopedia/newpage.html",{
            "form":form,
            "edit":form.fields["edit"],
            "entrytitle":form.fields["title"].initial
        })