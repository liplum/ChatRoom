using ChattingRoom.Server.Interfaces;

namespace ChattingRoom.Server.Services;
public class ResourceManager : IResourceManager {
    public string LogsFolder => new("Logs".InRootDir());

    public string SettingsFile => new("config.json".InRootDir());

    public void Initialize(IServiceProvider serviceProvider) {
    }
}