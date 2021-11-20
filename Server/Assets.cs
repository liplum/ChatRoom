using System.Dynamic;
using ChattingRoom.Server.Configs;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace ChattingRoom.Server;

public static class Assets
{
    private static readonly object _config_lock = new();
    public static Dictionary<string, ConfigItemT> AllBuiltInConfigs
    {
        get;
    } = new();
#nullable disable

    private static Configurations _configurations;
    public static Configurations Configurations
    {
        get
        {
            lock (_config_lock)
            {
                return _configurations;
            }
        }
        private set
        {
            lock (_config_lock)
            {
                _configurations = value;
            }
        }
    }

    public static dynamic Configs => Configurations;

    private static ExpandoObject _configJson;
#nullable enable
    public static void InitConfigs()
    {
        AddConfig(new("Port", 25000));
    }

    public static void AddConfig(ConfigItemT config)
    {
        AllBuiltInConfigs[config.Name] = config;
    }

    public static readonly string ConfigFile = "config.json".InRootDir();

    public static void LoadConfigs()
    {
        try
        {

            string content;
            if (ConfigFile.Exists())
            {
                content = File.ReadAllText(ConfigFile);
            }
            else
            {
                content = "{}";
            }

            _configJson = JsonConvert.DeserializeObject<ExpandoObject>(content, new ExpandoObjectConverter())!;
        }
        catch
        {
            _configJson = new ExpandoObject();
        }
        Configurations = new(_configJson!, AllBuiltInConfigs);
    }

    public static void SaveConfig()
    {
        EnsureConfig();
        var josnText = JsonConvert.SerializeObject(_configJson, Formatting.Indented);
        File.WriteAllText(ConfigFile, josnText);
    }

    private static void EnsureConfig()
    {
        foreach (var configName in AllBuiltInConfigs.Keys)
        {
            Configurations.TryGetValue(configName, out var _);
        }
    }

}
