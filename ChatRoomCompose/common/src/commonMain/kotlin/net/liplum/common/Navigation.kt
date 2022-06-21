package net.liplum.common

import com.arkivanov.essenty.parcelable.Parcelable
import com.arkivanov.essenty.parcelable.Parcelize

sealed class Scene: Parcelable {
    @Parcelize
    object ChatRoomList : Scene()
    @Parcelize
    object Chatting : Scene()
    @Parcelize
    object Login : Scene()
}