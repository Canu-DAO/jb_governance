# Governance Tracker

Simple bot to warn the juiceboxDAO of which day of the governance cycle it is. 

To add the bot simply click this [link](https://discord.com/api/oauth2/authorize?client_id=917818530513190922&permissions=292057827328&scope=bot), select the server you want to add the bot to and that's it.

## Config

Configuring the bot is also pretty straight forward, on data.json you simply set the json to
```
{
  CHANNEL_ID: <Id of the channel where you want the updates>
  CURRENT_DAY: <Number of the png file you want to be sent today (0-13, check on resources)>
  YESTERDAY_ID: 0 (no message was sent yesterday, so there's nothing to delete.)
}
```

If for some reason the bot key changes you also can change the ```DISCORD_KEY``` in the .env file.

## Changing the infographic

If you wish to change the infographic, simply head to [resources](https://github.com/Canu-DAO/jb_governance/tree/main/resources) and change the files in there.
