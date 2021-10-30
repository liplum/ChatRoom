namespace ChattingRoom.Core;
public interface IServiceProvider
{
    public In Reslove<In>();

    public void Inject(IInjectable injectable);

    public void Inject(object obj);
}
