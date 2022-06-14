package net.liplum.common

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBox
import androidx.compose.material.icons.filled.Send
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun App() {
    val appVm = AppVM()
    ChattingScreen(appVm)
}
@Composable
fun ChattingScreen(
    vm: AppVM,
) {
    var text by remember { mutableStateOf("") }
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
        },
        bottomBar = {
        },
        isFloatingActionButtonDocked = true,
        floatingActionButton = {
            FloatingActionButton(onClick = {
                vm.sendMsg(text)
                text = ""
            }) {
                Icon(Icons.Filled.Send, "")
            }
        }
    ) {
        Column {
            ChatMsgArea(vm)
            InputArea(vm, text) {
                text = it
            }
        }
    }
}
@Composable
fun ChatMsgArea(
    vm: AppVM,
) {
    Surface(
        shape = RoundedCornerShape(8.dp), elevation = 8.dp,
        modifier = Modifier.fillMaxWidth().fillMaxHeight(0.8f)
    ) {
        Conversation(vm, vm.allMessages)
    }
}
@Composable
fun Conversation(
    vm: AppVM,
    msgs: List<ChatMsg>,
) {
    LazyColumn {
        items(msgs) {
            ChatMsgCard(vm,it)
        }
    }
}
@Composable
fun ChatMsgCard(
    vm: AppVM,
    msg: ChatMsg,
) {
    val youUser by remember { vm.yourself }
    val isYourself = msg.userID == youUser.userID
    Row(
        modifier = Modifier.padding(all = 8.dp).fillMaxWidth(),
        horizontalArrangement = if (isYourself) Arrangement.End else Arrangement.Start
    ) {
        if (isYourself)
            ChatMsgCardText(msg, youUser)
        Icon(Icons.Filled.AccountBox, "")
        Spacer(modifier = Modifier.requiredWidth(8.dp))
        if (!isYourself)
            ChatMsgCardText(msg, youUser)
    }
}
@Composable
fun ChatMsgCardText(msg: ChatMsg, you: User) {
    var isExpanded by remember { mutableStateOf(false) }
    Column(modifier = Modifier.clickable {
        isExpanded = !isExpanded
    }) {
        Text(
            text = msg.userID,
            fontSize = Vars.textSize,
            color = if (msg.userID == you.userID)
                MaterialTheme.colors.primaryVariant
            else MaterialTheme.colors.secondaryVariant,
            style = MaterialTheme.typography.subtitle2,
        )
        Spacer(modifier = Modifier.requiredHeight(4.dp))
        Surface(shape = MaterialTheme.shapes.medium, elevation = 1.dp) {
            Text(
                text = msg.text,
                fontSize = Vars.textSize,
                modifier = Modifier.padding(all = 4.dp),
                style = MaterialTheme.typography.body2,
                maxLines = if (isExpanded) Int.MAX_VALUE else 1
            )
        }
    }
}
@Composable
fun InputArea(
    vm: AppVM,
    curInput: String,
    onInput: (String) -> Unit,
) {
    Surface(
        shape = RoundedCornerShape(8.dp), elevation = 8.dp,
        modifier = Modifier.fillMaxWidth().fillMaxHeight()
    ) {
        TextField(
            value = curInput,
            onValueChange = onInput,
            modifier = Modifier.fillMaxWidth().fillMaxHeight(),
        )
    }
}
