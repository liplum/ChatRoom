package net.liplum.common

import androidx.compose.foundation.Image
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.VectorPainter
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp

@Composable
fun App() {
    Row {
        Column {
            ChattingArea()
        }
    }
}
@Composable
fun ChattingArea() {
    Scaffold(
        topBar = {
        },
        bottomBar = {
        },
        isFloatingActionButtonDocked = true,
        floatingActionButton = {
            FloatingActionButton(onClick = {}) {
                Icon(Icons.Filled.Send, "")
            }
        }
    ) {
        Column {
            ChatMsgArea()
            InputArea()
        }
    }
}
@Composable
fun ChatMsgArea() {
    Surface(
        shape = RoundedCornerShape(8.dp), elevation = 8.dp,
        modifier = Modifier.requiredSize(500.dp)
    ) {
        Conversation(Vars.allMessages)
    }
}
@Composable
fun Conversation(msgs: List<ChatMsg>) {
    LazyColumn {
        items(msgs) {
            ChatMsgCard(it)
        }
    }
}
@Composable
fun ChatMsgCard(msg: ChatMsg) {
    Row(
        modifier = Modifier.padding(all = 8.dp).fillMaxWidth()
    ) {
        Icon(Icons.Filled.AccountBox, "")
        Spacer(modifier = Modifier.requiredWidth(8.dp))
        // We keep track if the message is expanded or not in this
        // variable
        var isExpanded by remember { mutableStateOf(false) }
        Column(modifier = Modifier.clickable {
            isExpanded = !isExpanded
        }) {
            Text(
                text = msg.userID,
                color = if (msg.userID == Vars.you.userID)
                    MaterialTheme.colors.primaryVariant
                else MaterialTheme.colors.secondaryVariant,
                style = MaterialTheme.typography.subtitle2,
            )
            Spacer(modifier = Modifier.requiredHeight(4.dp))
            Surface(shape = MaterialTheme.shapes.medium, elevation = 1.dp) {
                Text(
                    text = msg.text,
                    modifier = Modifier.padding(all = 4.dp),
                    style = MaterialTheme.typography.body2,
                    maxLines = if (isExpanded) Int.MAX_VALUE else 1
                )
            }
        }
    }
}
@Composable
fun InputArea() {
    Surface(
        shape = RoundedCornerShape(8.dp), elevation = 8.dp,
        modifier = Modifier.requiredHeight(200.dp).requiredWidth(500.dp)
    ) {
        val curInput = remember { mutableStateOf(TextFieldValue()) }
        TextField(
            value = curInput.value,
            onValueChange = { curInput.value = it },
            modifier = Modifier.requiredHeight(200.dp).requiredWidth(500.dp)
        )
    }
}
