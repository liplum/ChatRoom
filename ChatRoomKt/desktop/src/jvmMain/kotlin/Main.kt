import androidx.compose.material.MaterialTheme
import androidx.compose.material.darkColors
import androidx.compose.material.lightColors
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.DpSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.window.rememberWindowState
import net.liplum.common.App
import net.liplum.common.AppVM

fun main() = application {
    val vm = remember { AppVM() }
    val windowState = rememberWindowState()
    windowState.size = DpSize(500.dp, 720.dp)
    val isLightMode = remember { vm.isLightMode }
    MaterialTheme(
        colors = if (isLightMode.value) lightColors()
        else darkColors(primaryVariant = Color.White)
    ) {
        Window(
            state = windowState,
            onCloseRequest = ::exitApplication
        ) {
            App(vm)
        }
    }
}
