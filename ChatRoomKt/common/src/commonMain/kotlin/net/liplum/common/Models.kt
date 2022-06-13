package net.liplum.common

class ChatMsg {
    var userID = ""
    var text = ""
    var time = 0L

    companion object {
        val X = ChatMsg()
    }
}

class ChatRoom {
    var id = 0

    companion object {
        val X = ChatRoom()
    }
}

class User {
    var userID = ""
    companion object{
        val X = User()
    }
}