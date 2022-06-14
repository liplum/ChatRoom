package net.liplum.common

data class ChatMsg(
    val userID: String = "",
    val text: String = "",
    val time: Long = 0L,
) {
    companion object {
        val X = ChatMsg()
    }
}

data class ChatRoom(
    val id: Int = 0,
) {
    companion object {
        val X = ChatRoom()
    }
}

data class User(
    val userID: String = "",
) {
    companion object {
        val X = User()
    }
}