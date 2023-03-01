package net.liplum.common

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Send
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

@Composable
fun ChatRoomListScene(
    vm: AppVM,
    onSwitchRoom: (Int) -> Unit
) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar {

                SwitchDarkTheme(vm)
            }
        },
        bottomBar = {
        },
        isFloatingActionButtonDocked = true,
        floatingActionButton = {
            FloatingActionButton(onClick = {      }) {
                Icon(Icons.Filled.Add, "Create a chat room")
            }
        }
    ) {

    }
}

@Composable
fun ChatRoomList(
    chatRooms: List<ChatRoom>,
    onSwitchRoom: (Int) -> Unit
) {
    LazyColumn {
        items(chatRooms) {
            ChatRoom(it, onSwitchRoom)
        }
    }
}

@Composable
fun ChatRoom(
    room: ChatRoom,
    onSwitchRoom: (Int) -> Unit
) {
    Row {

    }
}
