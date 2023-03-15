import requests
import openai
import os
from dotenv import load_dotenv
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from .forms import CreateBlog
from .models import Blog, Comment
from .forms import BlogCommentForm
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Create your views here.
def index(request):
    return render(request, 'index.html')

def blogMain(request):
    blogs = Blog.objects.all()
    return render(request, 'blogMain.html', {'blogs': blogs})

def tistory(request):

    # bid = Blog.objects.count() - 1
    bid = int(request.POST['bid'])
    blogs = Blog.objects.filter(id=bid)

    # Post article to Tistory API
    params = {
        'access_token': os.environ.get("TISTORY_ACCESS_TOKEN"),
        'output': 'json',
        'blogName': os.environ.get("TISTORY_BLOG_NAME"),
        'title': blogs[0].title,
        'content': blogs[0].body,
        'visibility': '0',
        'tag': blogs[0].tag,
        'category': blogs[0].category
    }
    response = requests.post(os.environ.get("TISTORY_URL"), data=params)
    print(response)
    result = response.json()
    print(result)
    
    if result['tistory']['status'] == '200':
        print('Complete Article.')
    else:
        print(f'Error: {result["tistory"]["error_message"]}')

    return redirect('blogMain')


def createBlog(request):
 
    if request.method == 'POST':
        form = CreateBlog(request.POST)
 
        if form.is_valid():
            form.save()
            return redirect('blogMain')
        else:
            return redirect('index')
    else:
        form = CreateBlog()
        return render(request, 'createBlog.html', {'form': form})


def detail(request, blog_id):
    blog_detail = get_object_or_404(Blog, pk=blog_id)
    comments = Comment.objects.filter(blog_id=blog_id)
 
    if request.method == 'POST':
        comment_form = BlogCommentForm(request.POST)
 
        if comment_form.is_valid():
            content = comment_form.cleaned_data['comment_textfield']
 
            print(content)

            login_request_uri = 'https://kauth.kakao.com/oauth/authorize?'
 
            client_id = '595124ca7fc73d69ee0584c6535bc248'
            redirect_uri = 'http://127.0.0.1:8000/oauth'
            
            login_request_uri += 'client_id=' + client_id
            login_request_uri += '&redirect_uri=' + redirect_uri
            login_request_uri += '&response_type=code'

            request.session['client_id'] = client_id
            request.session['redirect_uri'] = redirect_uri
 
            return redirect(login_request_uri)
        else:
            return redirect('blogMain')
 
    else:
        comment_form = BlogCommentForm()
 
        context = {
            'blog_detail': blog_detail,
            'comments': comments,
            'comment_form': comment_form
        }
 
        return render(request, 'detail.html', context)

def oauth(request):
    code = request.GET['code']
    print('code = ' + str(code))

    client_id = request.session.get('client_id')
    redirect_uri = request.session.get('redirect_uri')
    
    access_token_request_uri = "https://kauth.kakao.com/oauth/token?grant_type=authorization_code&"
 
    access_token_request_uri += "client_id=" + client_id
    access_token_request_uri += "&redirect_uri=" + redirect_uri
    access_token_request_uri += "&code=" + code
    
    print(access_token_request_uri)

    access_token_request_uri_data = requests.get(access_token_request_uri)
    json_data = access_token_request_uri_data.json()
    access_token = json_data['access_token']
    print(access_token)

    user_profile_info_uri = "https://kapi.kakao.com/v1/api/talk/profile?access_token="
    user_profile_info_uri += str(access_token)
    
    user_profile_info_uri_data = requests.get(user_profile_info_uri)
    user_json_data = user_profile_info_uri_data.json()
    nickName = user_json_data['nickName']
    profileImageURL = user_json_data['profileImageURL']
    thumbnailURL = user_json_data['thumbnailURL']
    
    print("nickName = " + str(nickName))
    print("profileImageURL = " + str(profileImageURL))
    print("thumbnailURL = " + str(thumbnailURL))

    return redirect('blogMain')



def generate_response(prompt):
    """Generate a response from OpenAI's API"""
    response = openai.Completion.create(
        engine= os.environ.get("ENGINE"),
        prompt=prompt,
        temperature= os.environ.get("TEMPERATURE"),
        max_tokens= os.environ.get("MAX_TOKENS"),
        top_p= os.environ.get("TOP_P"),
        frequency_penalty= os.environ.get("FREQUENCY_PENALTY"),
        presence_penalty= os.environ.get("PRESENCE_PENALTY")
    )
    message = response.choices[0].text.strip()
    return message

def chatGPT(request):
    """Handle file upload and generate content for each row"""
    if request.method == 'POST':

        text1 = [request.POST['text'], request.POST['text2'], request.POST['text3']]

        for row in text1:
            text = row

            if text == "":
                return redirect('blogMain')

            # Generate different prompts and responses
            prompt1 = f"""
                write a blog about this movie. movie: {text}             
            """
            message1 = generate_response(prompt1)
            print(f"ChatGpt1:  {message1}")

            prompt2 = f"""
                write a blog about a good perspectives and detailed explanations when we watch this movie. Do not write explanations. movie: {text}
            """
            message2 = generate_response(prompt2)
            print(f"ChatGpt2:  {message2}")

            prompt3 = f"""
                write a 10 hashtags fit to this blog title, {text}. And don't write "#" in front of each hashtags. And connect each hashtags with comma(,).
            """
            message3 = generate_response(prompt3)
            print(f"ChatGpt3:  {message3}")
            # papagoResponse3 = requests.post(settings.PAPAGO_URL, headers=settings.HEADERS, data={"source": "en", "target": "ko", "text": message3})
            # papagoResult3 = papagoResponse3.json()["message"]["result"]["translatedText"]

            prompt4 = f"""
                write a specific 3 examples of people's reactions to this movie. movie: {text}
            """
            message4 = generate_response(prompt4)
            print(f"ChatGpt4:  {message4}")

            prompt5 = f""" Put them together and write a long movie blog post. At least 2000 words. Do not write explanations. Write all in HTML code.
                '{message1}', '{message2}', '{message4}'
            """
            message5 = generate_response(prompt5)
            print(f"ChatGpt5:  {message5}")

            # Save conversation to database
            insertConversation = Blog(title=text, body=message5, tag=message3, category=os.environ.get("CATEGORY_ID"))
            insertConversation.save()

        return redirect('blogMain')
    else:
        return render(request, 'chatGPT.html')



# def conversation_list(request):
#     # conversation = ModelConversation.objects.all()
#     getConversation = ModelConversation.objects.get(id=1)
#     print(getConversation)

#     return render(request, 'editor.html', {'conversation': getConversation})

