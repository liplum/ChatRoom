import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import net.liplum.common.App

fun main() = application {
    Window(onCloseRequest = ::exitApplication) {
        App()
    }
}
