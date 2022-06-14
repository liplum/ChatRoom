package net.liplum.common

import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf

class AppVM {
    var yourself = mutableStateOf(User("Liplum"))
    var allMessages = mutableStateListOf<ChatMsg>()
    var curChatRoom = mutableStateOf(ChatRoom())
    var allChatRooms = mutableStateListOf<ChatRoom>()
    fun sendMsg(text: String) {
        allMessages.add(
            ChatMsg(
                userID = yourself.value.userID,
                text = text,
            )
        )
    }
}