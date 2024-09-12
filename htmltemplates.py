css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex 
}
.chat-message.user {
    background-color: #d2d9d9;
    color: #000000;
    font-size:20px;
}
.chat-message.bot {
    background-color: #d2d9d9;
    color:#000000;
    font-size:20px;
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 42px;
  max-height: 42px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #000000;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://t3.ftcdn.net/jpg/02/15/61/92/360_F_215619203_9mmrDaPnSHOUBfz9XVkjBAknw5XFEK0D.jpg" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://cdn.pixabay.com/photo/2021/07/02/04/48/user-6380868_640.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''