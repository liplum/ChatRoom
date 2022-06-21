package net.liplum.common

import androidx.compose.runtime.*
import com.arkivanov.decompose.ExperimentalDecomposeApi
import com.arkivanov.decompose.extensions.compose.jetbrains.Children
import com.arkivanov.decompose.extensions.compose.jetbrains.animation.child.childAnimation
import com.arkivanov.decompose.extensions.compose.jetbrains.animation.child.fade
import com.arkivanov.decompose.extensions.compose.jetbrains.animation.child.plus
import com.arkivanov.decompose.extensions.compose.jetbrains.animation.child.scale
import com.arkivanov.decompose.router.pop
import com.arkivanov.decompose.router.push

@Composable
fun App(vm: AppVM) {
    var screenState by remember { mutableStateOf<Scene>(Scene.ChatRoomList) }
    when (val screen = screenState) {
        is Scene.ChatRoomList -> ChatRoomListScene(vm) {
            vm.switchChatRoom(it)
            screenState = Scene.Chatting
        }
        is Scene.Chatting -> ChattingScene(vm) {
            screenState = Scene.ChatRoomList
        }
    }
}

@Suppress("EXPERIMENTAL_IS_NOT_ENABLED")
@OptIn(ExperimentalDecomposeApi::class)
@Composable
fun Rooting(vm: AppVM) {
    // Create and remember the Router
    val router = rememberRouter<Scene>(
        initialConfiguration = Scene.ChatRoomList  // Start with the List screen
    )
    // Render children
    Children(
        routerState = router.state,
        animation = childAnimation(scale() + fade())
    ) { screen ->
        when (val configuration = screen.configuration) {
            is Scene.Login -> LoginScene {
                vm.login(it)
            }
            is Scene.ChatRoomList -> ChatRoomListScene(vm) {
                vm.switchChatRoom(it)
                router.push(Scene.Chatting)
            }
            is Scene.Chatting -> ChattingScene(vm) {
                router.push(Scene.Chatting)
            }
        }.let {} // Ensure exhaustiveness
    }
}