package net.liplum.android

import net.liplum.common.App
import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.material.MaterialTheme
import androidx.compose.material.darkColors
import androidx.compose.material.lightColors
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.Color
import net.liplum.common.AppVM

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val vm = remember { AppVM() }
            val isLightMode = remember { vm.isLightMode }
            MaterialTheme(
                colors = if (isLightMode.value) lightColors()
                else darkColors(primaryVariant = Color.White)
            ) {
                App(vm)
            }
        }
    }
}