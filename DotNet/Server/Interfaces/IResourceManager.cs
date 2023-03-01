namespace ChattingRoom.Server.Interfaces;
public interface IResourceManager : IInjectable {
    public string LogsFolder {
        get;
    }

    public string SettingsFile {
        get;
    }
}