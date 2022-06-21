package net.liplum.common

import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.LocalSaveableStateRegistry
import androidx.compose.runtime.saveable.SaveableStateRegistry
import com.arkivanov.decompose.ComponentContext
import com.arkivanov.decompose.DefaultComponentContext
import com.arkivanov.decompose.router.Router
import com.arkivanov.decompose.router.router
import com.arkivanov.essenty.backpressed.BackPressedDispatcher
import com.arkivanov.essenty.lifecycle.Lifecycle
import com.arkivanov.essenty.lifecycle.LifecycleRegistry
import com.arkivanov.essenty.lifecycle.destroy
import com.arkivanov.essenty.lifecycle.resume
import com.arkivanov.essenty.parcelable.Parcelable
import com.arkivanov.essenty.parcelable.ParcelableContainer
import com.arkivanov.essenty.statekeeper.StateKeeper
import com.arkivanov.essenty.statekeeper.StateKeeperDispatcher

@Composable
inline fun <reified C : Parcelable> rememberRouter(
    initialConfiguration: C,
    handleBackButton: Boolean = false,
): Router<C, Any> {
    val context = rememberComponentContext()

    return remember {
        context.router(
            initialConfiguration = initialConfiguration,
            handleBackButton = handleBackButton
        ) { configuration, _ ->
            configuration
        }
    }
}
@Composable
inline fun <reified C : Parcelable> rememberRouter(
    noinline initialStack: () -> List<C>,
    handleBackButton: Boolean = false,
): Router<C, Any> {
    val context = rememberComponentContext()

    return remember {
        context.router(
            initialStack = initialStack,
            handleBackButton = handleBackButton
        ) { configuration, _ ->
            configuration
        }
    }
}
@Composable
fun rememberComponentContext(): ComponentContext {
    val lifecycle = rememberLifecycle()
    val stateKeeper = rememberStateKeeper()
    val backPressedDispatcher = LocalBackPressedDispatcher.current ?: BackPressedDispatcher()

    return remember {
        DefaultComponentContext(
            lifecycle = lifecycle,
            stateKeeper = stateKeeper,
            backPressedHandler = backPressedDispatcher
        )
    }
}
@Composable
private fun rememberLifecycle(): Lifecycle {
    val lifecycle = remember { LifecycleRegistry() }

    DisposableEffect(Unit) {
        lifecycle.resume()
        onDispose { lifecycle.destroy() }
    }

    return lifecycle
}
@Composable
private fun rememberStateKeeper(): StateKeeper {
    val saveableStateRegistry: SaveableStateRegistry? = LocalSaveableStateRegistry.current
    val dispatcher =
        remember {
            StateKeeperDispatcher(saveableStateRegistry?.consumeRestored(KEY_STATE) as ParcelableContainer?)
        }

    if (saveableStateRegistry != null) {
        DisposableEffect(Unit) {
            val entry = saveableStateRegistry.registerProvider(KEY_STATE, dispatcher::save)
            onDispose { entry.unregister() }
        }
    }

    return dispatcher
}

val LocalBackPressedDispatcher: ProvidableCompositionLocal<BackPressedDispatcher?> =
    staticCompositionLocalOf { null }
private const val KEY_STATE = "STATE"
