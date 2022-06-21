package net.liplum.common
import androidx.compose.desktop.ui.tooling.preview.Preview
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
actual fun getPlatformName(): String
= "Desktop"

@Preview
@Composable
fun AppPreview() {
    val vm = remember { AppVM() }
    App(vm)
}