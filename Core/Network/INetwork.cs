using System.Diagnostics.CodeAnalysis;

namespace ChattingRoom.Core.Networks;
public interface INetwork : IInjectable, IMessageChannelContainer
{
    public void SendDatapackTo([NotNull] IDatapack datapack, [NotNull] NetworkToken token);

    public void RecevieDatapack([NotNull] IDatapack datapack);

    public void StartService();

    public void StopService();
}
