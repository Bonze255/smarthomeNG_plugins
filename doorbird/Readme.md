#!/bin/bash

Doorbell.sh script
##############################################################
##                                                          ##
##  Doorbell.sh script                                      ##
##  Send Doorbird D101S pictures to telegram message script ##
##                                                          ##
##############################################################



# Telegram configuration
TelegramUser01="Activated"
TelegramUser02="Desactivated"
TelegramUser03="Desactivated"

Token_1="xxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
Token_2="xxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
Token_3="xxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

ChatID1="xxxxxxxxx"
ChatID2="xxxxxxxxx"
ChatID3="xxxxxxxxx"


# Doorbird D101S configuration
DoorbirdIP="xxx.xxx.xxx.xxx"
DoorbirdLogin="xxxxxx0001"
DoorbirdPassword="xxxxxxxxxx"
DoorbirdUrlImage="http://$DoorbirdIP/bha-api/image.cgi?http-user=$DoorbirdLogin&http-password=$DoorbirdPassword"
DoorbirdUrlHistory="http://$DoorbirdIP/bha-api/history.cgi?index=1&http-user=$DoorbirdLogin&http-password=$DoorbirdPassword"


# Snapshot configuration
SnapFile1="/var/tmp/DoorbirdSnapshot1.jpg"
SnapFile2="/var/tmp/DoorbirdSnapshot2.jpg"
SnapFile3="/var/tmp/DoorbirdSnapshot3.jpg"
PauseBetweenSnap=2





#Script beginning
###########################################################################################################################################


# send telegram (text only)

if [ "$TelegramUser01" == "Activated" ]
	then curl -s -X POST "https://api.telegram.org/bot$Token_1/sendMessage?chat_id=$ChatID1&text=Baptiste, Quelqu'un vient de sonner à la porte !"
fi

if [ "$TelegramUser02" == "Activated" ]
	then curl -s -X POST "https://api.telegram.org/bot$Token_2/sendMessage?chat_id=$ChatID2&text=Noémie, Quelqu'un vient de sonner à la porte !"
fi

if [ "$TelegramUser03" == "Activated" ]
	then curl -s -X POST "https://api.telegram.org/bot$Token_3/sendMessage?chat_id=$ChatID3&text=Quelqu'un vient de sonner à la porte !"
fi





# get second Picture
wget -O $SnapFile2 $DoorbirdUrlImage


# pause
sleep $PauseBetweenSnap


# get another Picture
wget -O $SnapFile3 $DoorbirdUrlImage


# pause
sleep $PauseBetweenSnap


# get first Picture
wget -O $SnapFile1 $DoorbirdUrlImage



# send telegram (multiple pictures) to user 1
if [ "$TelegramUser01" == "Activated" ]
	then curl -s \
		-X POST "https://api.telegram.org/bot"$Token_1"/sendMediaGroup" \
		-F chat_id=$ChatID1 \
		-F media='[{"type":"photo","media":"attach://photo_1","caption":"When Doorbell button was pressed"},{"type":"photo","media":"attach://photo_2","caption":"Other picture 1"},{"type":"photo","media":"attach://photo_3","caption":"Other picture 2"}]' \
		-F photo_1="@$SnapFile1" \
		-F photo_2="@$SnapFile2" \
		-F photo_3="@$SnapFile3"
fi

# send telegram (multiple pictures) to user 2
if [ "$TelegramUser02" == "Activated" ]
	then curl -s \
		-X POST "https://api.telegram.org/bot"$Token_2"/sendMediaGroup" \
		-F chat_id=$ChatID2 \
		-F media='[{"type":"photo","media":"attach://photo_1","caption":"When Doorbell button was pressed"},{"type":"photo","media":"attach://photo_2","caption":"Other picture 1"},{"type":"photo","media":"attach://photo_3","caption":"Other picture 2"}]' \
		-F photo_1="@$SnapFile1" \
		-F photo_2="@$SnapFile2" \
		-F photo_3="@$SnapFile3"
fi

# send telegram (multiple pictures) to user 3
if [ "$TelegramUser03" == "Activated" ]
	then curl -s \
		-X POST "https://api.telegram.org/bot"$Token_3"/sendMediaGroup" \
		-F chat_id=$ChatID3 \
		-F media='[{"type":"photo","media":"attach://photo_1","caption":"When Doorbell button was pressed"},{"type":"photo","media":"attach://photo_2","caption":"Other picture 1"},{"type":"photo","media":"attach://photo_3","caption":"Other picture 2"}]' \
		-F photo_1="@$SnapFile1" \
		-F photo_2="@$SnapFile2" \
		-F photo_3="@$SnapFile3"
fi


# Delete all pictures
rm $SnapFile1
rm $SnapFile2
rm $SnapFile3

