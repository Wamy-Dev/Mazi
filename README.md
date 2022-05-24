# Mazi
A discord bot to watch plex with your friends.

# Only trust the bot @Mazi#2364 with your data!
People may try to impersonate the bot to try and steal your information, but until I make a new linking system, only trust the bot @Mazi#2364.
# How does this work?
1. First you connect your plex account with discord and choose which library you would like to share from.
2. Then when you and your friends want to watch a movie, you choose whether you want to make a poll to decide the movie or you search for a movie yourself.
3. The bot then automatically creates a watch together session with an invite link.
4. The bot then waits 10 minutes for everyone to join and lists how many users are in currently. 
5. Then after the 10 minutes, the movie or show automatically starts and then the user who owns the media can choose the controls.

# Features
- [ ] Easy Plex and Discord Linking
- [ ] Beautiful
- [ ] Ease of Use
- [ ] Fast

# Safety
For those who want to host your own watch together session with friends, a linked plex account is required. When you run ```>link``` the bot dms you for your credentials and tests them. If the test is successful, the bot encrypts them with Argon2id, and stores them in a secure database. You can always run ```>unlink``` to unlink your accounts which deletes them from the database.
