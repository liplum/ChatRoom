package net.liplum.common

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.tooling.preview.Preview

actual fun getPlatformName(): String =
    "Android"

@Preview
@Composable
fun AppPreview() {
    val vm = remember { AppVM() }
    App(vm)
}