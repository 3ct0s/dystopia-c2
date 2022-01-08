# Setup guide for Disctopia

Please follow the following steps to setup Disctopia.

 ## Step 1# Create the Server

You need to create a Discord server using [this](https://discord.com/template/XFNKt38yzXKC) template.

You should get this on Discord after clicking the link:
![image](https://i.ibb.co/WczCgPZ/Capture.png)
Give your server a name and click on the "Create" button.

## Step 2# Create the Webhooks

You need to create 2 Discord Webhooks from your **Servers Settings >> Intergrations >> Webhooks.**

- Name the first one **"Keylogger"** and set it's channel to **"keylogs"**

![image](https://i.ibb.co/RBmNS3K/Capture.png)

- Name the second one "Token" and set it's channel to **"tokens"**

![image](https://i.ibb.co/wccPgCx/Capture.png)

## Step 3# Create the Bot

 You need to create a Discord Bot from the **discord developer portal.** So make sure you are connected to Discord from the Web Browser and head over to [this](https://discordapp.com/developers/applications/me) page and click on **"New Application."**

![image](https://i.ibb.co/JKg1Y9c/Capture.png)

Then you need to give your application a name and click on **"Create"**.

![image](https://i.ibb.co/W5BhCvv/Capture.png)

Now from the settings on the left, you need to click on **"Bot"** and then **"Add Bot"**.

![image](https://i.ibb.co/zSm3Jsz/Capture.png)

The last thing you can do is to customize the bot. Change its name, its avatar etc.

![image](https://i.ibb.co/b3YJmBq/Capture.png)

Make sure you scroll down and enable the 3 options from the **Privileged Gateway Intents** section.

![image](https://i.ibb.co/f2P9KgQ/Capture.png)

## Step 4# Invite the Bot

Now you need to invite the bot to your server. Head to the [application page](https://discord.com/developers/applications) and click on the Application that you just created. Then click on the **OAuth2 tab** list and click on the **URL Generator** tab.

![image](https://i.ibb.co/x65JKxm/Capture.png)

Now you need to select the **bot** option from the scopes and the **Administrator** option from the bot permissions.

![image](https://i.ibb.co/qYVftpR/Capture.png)

The last thing you need to do is to copy the **URL** from the bottom of the page and paste it on your browser.

![image](https://i.ibb.co/FWGSXqS/Capture.png)

Now access the link that you coppied and you should see th bot invitation page. From the **"Add to serrver"** drop down menu make sure you select the server that yuo just created and click on **Continue**. You will also be asked to **Authorize** access to the bot and complete a CAPTCHA.

![image](https://i.ibb.co/hgqLsVB/Capture.png)

Once you are done with these you should see your Bot on your server.


## Step 5# Enable developer mode

You will need to enable the developer option for your Discord account. To do that head to your **Account Settings >> Advanced** and Enable **Developer Mode**

![image](https://i.ibb.co/BKnvn8H/Discord-Web-Enable-Developer-Mode.png)


## Build the Backdoor

Now you can move to the next step which is building the backdoor. Follow the [build guide](BUILD.md) to build the backdoor.
