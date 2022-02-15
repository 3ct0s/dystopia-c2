# Disctopia Help Command

## Available commands

- **!cmd {AGENT-ID} {COMMAND}**

    With the !cmd command you can run your own commands on the agent. If an agent-id is not specified, the command will be run on all agents.

- **!cd {AGENT-ID} {PATH}**
    
    With the !cd command you can change the working directory of the agent.

- **!webshot {AGENT-ID}**

    With the !webshot command you can take a snapshot of the agent's webcam (If there is one).
- **!process {AGENT-ID}**

    With the !process command you can view all the process on the agent.

- **!download {AGENT-ID} {PATH}**

    With the !download command you can download a file from the agent. You will need to specify the full path to the file.

    Downloads will be saved on the **#downloads** channel.

- **!upload {AGENT-ID} {URL} {NAME}**

    With the !upload command you can upload a file to the agent. You will need to specify a direct download link to the file.

    Uploads can be found on the `C:\Users\USERNAME\.config\uploads` directory.

- **!token {AGENT-ID}**

    With the !token command you can get the stored Discord Tokens from the agent.

    The tokens will be saved on the **#tokens** channel.

- **!screenshot {AGENT-ID}**

    With the !screenshot command you can take a screenshot of the agents screen.

    Screenshots will be saved on the **#screenshots** channel.

- **!keylog {AGENT-ID} {REPORT-EVERY}**

    With the !keylog command you initiate the keylogger on the specified agent. Make sure you add how often the keylogger will report to you in SECONDS.

    Keylogs will be saved on the **#keylogs** channel.

- **!credentials {AGENT-ID}**

    With the !credentials command you will get the stored chrome credentials from the agent.

    Credentials will be saved on the **#credentials** channel.

- **!persistent {AGENT-ID}**

    With the !persistence command you will enable persistence on the target agent.

- **!ls**

    With the !ls command you will get the list of all the online agents.

- **!terminate {AGENT-ID}**

    With the !terminate command you will terminate the agent connection.
