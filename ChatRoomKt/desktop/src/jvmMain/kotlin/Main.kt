import androidx.compose.material.MaterialTheme
import androidx.compose.ui.unit.DpSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState
import net.liplum.common.App

fun main() = application {
    val windowState = rememberWindowState()
    windowState.size = DpSize(500.dp, 720.dp)
    MaterialTheme {
        Window(
            state = windowState,
            onCloseRequest = ::exitApplication
        ) {
            App()
        }
    }
}
