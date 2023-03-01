namespace ChatRoom.Core.Network;
public interface INetwork : IInjectable, IMessageChannelContainer {

    public delegate void OnClientConnectedHandler(NetworkToken token);

    public delegate void OnClientDisconnectedHandler(NetworkToken token);

    public delegate void OnMessagePreAnalyzeHandler(NetworkToken? token, string sourceText, dynamic json);

    public IEnumerable<NetworkToken> AllConnectedClient {
        get;
    }
    public void SendDatapackTo(IDatapack datapack, NetworkToken token);

    public void RecevieDatapack(IDatapack datapack, NetworkToken? token = null);

    public void StartService();

    public void StopService();

    public bool IsConnected(NetworkToken token);

    public event OnClientConnectedHandler OnClientConnected;

    public event OnClientDisconnectedHandler OnClientDisconnected;

    public event OnMessagePreAnalyzeHandler OnMessagePreAnalyze;
}