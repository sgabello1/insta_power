# Generative AI Tools for Content Creation


This are a few cool scripts to help you have fun with content creation and generative AI. 
In particular:
1. get-nuz.py &rarr; this script help you to find the best news and YouTube videos according to the keyword you search for
   ![image](https://github.com/user-attachments/assets/1e1af571-e8e7-49aa-a7df-f39378bad967)

3. ui-create.py &rarr; it s a UI that present to tabs.
   2.a  "YouTube Short". Download the requested YouTube video, you can select the amount of words to aumatically generate the caption (coming from the YT description). If you add some text in the section "Voice over text" and check "Generate Captions" it will automatically generate a female voice on the video and related captions. You can adjust the size of the font on the video. If you check "Adapt Captions" the voice will etiher speed up or slow down accoridng to the video lenght. Apply filter will filter the downloaded video with a cool FFMPEG filter inspired by Canva's filter "Festive". 
    ![image](https://github.com/user-attachments/assets/38c5fd99-c742-4883-a2af-b6afcb69de2a)

   2.b  "Story from Article". Fetch the text from the article and build a nice caption with 29 hashatag, with a special prompt.
   
   ![image](https://github.com/user-attachments/assets/03d2582d-452c-4895-98a4-437d187d3925)

  This is how i formatted the prompt
  
  >"Article content:\n{text}"
  > **Find me:why is this video description is interesting?Identify key elements that evoke emotions and make the reader engaged.Why should the reader care?**"
  > **Add some shocking fact based on the data from Internet or your knowledge related to China, innovation, robotics and AI or drama to make the story more interesting and gripping. Underline how the proposed solution make it as an improvement to the problem you just stated**"
  > "Deliver a concise but powerful summary, written with very easy words, stating the problem first and then the solution, in max {words_number} words of the article written with the sytle of the famous copywriter Tim Denning."
  > "Provide a well-researched list of at least 29 hashtags to maximize reach. Write them one after the other dont add numbers or lists.\"
  > "Now keep only the last two answers combined and add between the caption and the hashtags the sentence '\n\n FOLLOW ME FOR INCREDIBLE CHINA.ROBOTICS!!!\n\n'. Make sure is well readable and spaced."


# Live Demo Here! 

[https://insta-pawa.com](https://bit.ly/3Dt0lIb)

Note: It can be a bit slow due to the free tier service im using ;)

 ![image](https://github.com/user-attachments/assets/06e30e47-dbdb-4665-9f06-426400490156)

 

# Notes

When you try the scripts on your computer make sure you put the OpenAI, Youtube and Google News APIs in the hidden file ".env" on your computer. 

   
