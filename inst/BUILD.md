# Disctopia Build Guide

## Step 1# Open the settings.json File

On your machine open the settings.json file with any text editor. You should see this:

![image](https://i.ibb.co/cyFYKmr/Capture.png)

## Step 2# Edit the settings.json File

You will need to edit the settings.json file to add the values to all the fields.

- ### Name the backdoor 
    Change the name from **"None"** to whatever you want. Make sure you **DON'T** include the ".exe" extension as it is automatically added to the file.

- ### Add the Bot token
    Change the token from "None" to the one from your recently created bot. To do that head over to the [discord developer portal](https://discordapp.com/developers/applications) and click on the application that you just created. Then click on the **Bot** tab and click on the **Copy** button from the **"Token"** section.

    ![image](https://i.ibb.co/tXqVCr8/Capture.png)

    Once you have the token add that to the **settings.json** file on the **"bot-token"** field.

- ### Add the Token and Keylogger Webhooks
    Earlier on the Setup Guide you created the webhooks for the Keylogger and the Token. Now you need to add the webhooks to the settings.json file.

    To access them, head over to your new server's settings and click on the **"Intergrations"** tab. Then click on the **"Webhooks"** tab.

    Get the **Webhook URLs** for both the **Keylogger and the Token** and add them to the settings.json file.

    ![image](https://i.ibb.co/s20C1DM/Capture.png)

- ### Add the Channel IDs 

    You will need to get the channel ID from the following channels in
    your server: `screenshots, downloads, agent-online, credentials`

    To do that, right click on the channel and click on the last option **"Copy ID"**.

    ![image](https://i.ibb.co/T0Lht6J/Capture.png)

    Once you have the ID you need to add that to the settings.json file. You need to do the same thing for all the channels mentioned above.

- ### Add Automatic Keylogger
    
    You will need to add the **"True"** or **"False"** to the **"auto-keylogger"** field. This will tell the backdoor to run the keylogger automactically or not when the backdoor is executed.

### Edited file Example

Once you are done editing your settings.json file, you can save it and and have an end result like this:

![image](https://i.ibb.co/L8dT8Wv/Capture.png)

## Step 3# Run the builder.py Script

Now that we have saved all the settings, we can run the builder.py script.

To Execute the builder.py script, you need to run the following command:
### Windows
```
.\venv\Scripts\python.exe builder.py
```
### Linux
```
sudo python3 builder.py
```

> If you ever need help with the commands execute the `help` command you will get the help menu

Once it executes you will need to run the `fetch` command to fetch the settings from the **settings.json** file.


Once you fetch the settings you can run the `config` command to view the settings.

![image](https://i.ibb.co/Bz0qrRv/Capture.png)


## Step 4# Build the Backdoor

Once you have everything ready and setup, execute the `build` command to build the backdoor.

You will be asked whether if everything is setup correctly. If it is, you can proceed to build the backdoor by entering the letter **Y** and pressing enter.

![image](https://i.ibb.co/7GFLbgf/Capture.png)

## Step 5# Find the Backdoor

Once the builder is done, you will find your generated backdoor in the **dist** directory.
