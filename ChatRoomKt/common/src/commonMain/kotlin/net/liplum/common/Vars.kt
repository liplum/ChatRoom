package net.liplum.common

object Vars {
    var you = User().apply {
        userID = "Liplum"
    }
    var curChatRoom = ChatRoom.X
    var allMessages = ArrayList<ChatMsg>().apply {
        add(ChatMsg().apply {
            userID = "liplum%1"
            text = "HHHHHHHHHH"
        })
        add(ChatMsg().apply {
            userID = "liplum$2"
            text = "AAAAAAAAAAssssssssssss\nsssssssss\nssssssssddddssss\n\ndsdssd"
        })
        add(ChatMsg().apply {
            userID = "Liplum"
            text = "Hello, plum!"
        })
        add(ChatMsg().apply {
            userID = "liplum#3"
            text = "fdsfghdkgfhsdiog"
        })
    }
}