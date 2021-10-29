using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface INetwork : IInjectable, IMessageChannelContainer
{
    public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token);

    public void RecevieDatapack([NotNull] IDatapack datapack, [AllowNull] NetworkToken token = null);

    public void StartService();

    public void StopService()
    {

    }

    public event OnClientConnectedHandler OnClientConnected;

    public delegate void OnClientConnectedHandler([NotNull] NetworkToken token);
}
