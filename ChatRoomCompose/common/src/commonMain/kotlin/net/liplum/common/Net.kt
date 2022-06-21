package net.liplum.common

import androidx.compose.runtime.mutableStateOf
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import java.net.Socket
import java.io.DataOutputStream
import kotlin.coroutines.CoroutineContext

class Net : CoroutineScope {
    private val defaultPort = 25000
    override val coroutineContext: CoroutineContext = Dispatchers.Main
    val msgToSocket = Channel<String>()
    var connectionStatus = mutableStateOf(false)
    var keepConnection = mutableStateOf(true)
    fun connectTo(ip: String, port: Int = defaultPort) = this.launch {
        try {
            val connection = Socket(ip, port)
            connection.setSoTimeout(4500)
            val stream = DataOutputStream(connection.getOutputStream())
            connectionStatus.value = true
            while (keepConnection.value) {
                try {
                    if (connectionStatus.value) {
                        stream.writeUTF(msgToSocket.receive())
                        stream.flush()
                    }
                } catch (e: Exception) {
                    connectionStatus.value = false
                    e.printStackTrace()
                }
            }
            stream.close()
            connection.close()
        } catch (e: Exception) {
            connectionStatus.value = false
        }
    }
}