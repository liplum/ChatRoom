using System.Dynamic;
using ChattingRoom.Server.Configs;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace ChattingRoom.Server;
public static class Assets {
    private static readonly object ConfigLock = new();

    public static readonly string ConfigFile = "config.json".InRootDir();
    private static Dictionary<string, ConfigItemT> AllBuiltInConfigs {
        get;
    } = new();
    public static void InitConfigs() {
        AddConfig(new("Port", 25000));
    }

    public static void AddConfig(ConfigItemT config) {
        AllBuiltInConfigs[config.Name] = config;
    }

    public static void LoadConfigs() {
        try {

            string content;
            if (ConfigFile.Exists()) content = File.ReadAllText(ConfigFile);
            else content = "{}";

            _configJson = JsonConvert.DeserializeObject<ExpandoObject>(content, new ExpandoObjectConverter())!;
        }
        catch {
            _configJson = new();
        }
        Configurations = new(_configJson!, AllBuiltInConfigs);
    }

    public static void SaveConfig() {
        EnsureConfig();
        var jsonText = JsonConvert.SerializeObject(_configJson, Formatting.Indented);
        File.WriteAllText(ConfigFile, jsonText);
    }

    private static void EnsureConfig() {
        foreach (var configName in AllBuiltInConfigs.Keys) Configurations.TryGetValue(configName, out var _);
    }
#nullable disable

    private static Configurations _configurations;

    private static Configurations Configurations {
        get {
            lock (ConfigLock) {
                return _configurations;
            }
        }
        set {
            lock (ConfigLock) {
                _configurations = value;
            }
        }
    }

    public static dynamic Configs => Configurations;

    private static ExpandoObject _configJson;
#nullable enable
}