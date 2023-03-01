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

data class LoginInfo(
    val serverIP: String,
    val port: String,
    /** aka, [User.userID]  */
    val account: String,
    val password: String
)