using System;
using System.Collections.Generic;
using System.Linq;
using Vintagestory.API.Client;
using Vintagestory.API.Common;
using Vintagestory.API.Datastructures;
using Vintagestory.API.MathTools;

namespace Automacao
{
    /// <summary>
    /// Desenha as partes que se mexem / acendem / aparecem conforme o modo — tudo descrito no atributo "partes"
    /// do bloco, gerado a partir do visualizador (mesmas animações: spin, swing, shake, slide, bob, viagem).
    /// </summary>
    public class MaquinaRenderer : IRenderer
    {
        class Anim
        {
            public string Tipo, Eixo;
            public float Speed, Amp, Freq, Dist, Periodo;
            public string[] When;
            public float T;
        }

        class Parte
        {
            public string Nome;
            public Vec3f Pivo;
            public MeshRef Off, On;
            public List<Anim> Anims = new List<Anim>();
            public string[] Show;
        }

        readonly ICoreClientAPI capi;
        readonly BEMaquina be;
        readonly List<Parte> partes = new List<Parte>();
        readonly Matrixf mat = new Matrixf();
        readonly string[] modos;
        readonly string[] glowModos;

        public double RenderOrder => 0.5;
        public int RenderRange => 64;

        public MaquinaRenderer(ICoreClientAPI capi, BEMaquina be)
        {
            this.capi = capi;
            this.be = be;
            var block = capi.World.BlockAccessor.GetBlock(be.Pos);
            var attr = block?.Attributes;
            modos = attr?["modos"].AsArray<string>() ?? new[] { "parado", "ligado" };
            glowModos = attr?["glowModos"].AsArray<string>();
            string key = attr?["chave"].AsString() ?? block?.Code?.FirstCodePart();
            if (attr == null || !attr["partes"].Exists) return;

            foreach (var p in attr["partes"].AsArray())
            {
                var parte = new Parte
                {
                    Nome = p["nome"].AsString(),
                    Show = p["show"].Exists ? p["show"].AsArray<string>() : null,
                };
                var pv = p["pivo"].AsArray<float>() ?? new float[] { 8, 0, 8 };
                parte.Pivo = new Vec3f(pv[0], pv[1], pv[2]);
                parte.Off = Load(block, key + "/" + parte.Nome);
                if (p["luz"].AsBool()) parte.On = Load(block, key + "/" + parte.Nome + "-on");
                foreach (var a in p["anim"].AsArray() ?? Array.Empty<JsonObject>())
                {
                    var an = new Anim
                    {
                        Speed = a["speed"].AsFloat(float.NaN),
                        Amp = a["amp"].AsFloat(float.NaN),
                        Freq = a["freq"].AsFloat(float.NaN),
                        Dist = a["dist"].AsFloat(8),
                        Periodo = a["periodo"].AsFloat(10),
                        When = a["when"].Exists ? a["when"].AsArray<string>() : null,
                    };
                    foreach (var tipo in new[] { "spin", "swing", "shake", "slide", "bob", "viagem" })
                        if (a[tipo].Exists) { an.Tipo = tipo; an.Eixo = a[tipo].AsString(); }
                    if (an.Tipo != null) parte.Anims.Add(an);
                }
                partes.Add(parte);
            }
        }

        MeshRef Load(Block block, string file)
        {
            var shape = Shape.TryGet(capi, new AssetLocation("automacao", "shapes/block/" + file + ".json"));
            if (block == null || shape == null) return null;
            capi.Tesselator.TesselateShape(block, shape, out MeshData mesh);
            return capi.Render.UploadMesh(mesh);
        }

        float RotY()
        {
            var b = capi.World.BlockAccessor.GetBlock(be.Pos);
            switch (b?.Variant?["side"])
            {
                case "east": return 90;
                case "north": return 180;
                case "west": return 270;
                default: return 0;
            }
        }

        bool Ligado(Anim an, string modo) => an.When != null ? an.When.Contains(modo) : modo != modos[0];

        public void OnRenderFrame(float dt, EnumRenderStage stage)
        {
            if (partes.Count == 0) return;
            string modo = string.IsNullOrEmpty(be.ModoAtual) ? modos[0] : be.ModoAtual;
            bool brilha = glowModos != null ? glowModos.Contains(modo) : be.Energizado;

            var rpi = capi.Render;
            var cam = capi.World.Player.Entity.CameraPos;
            rpi.GlDisableCullFace();
            var prog = rpi.PreparedStandardShader(be.Pos.X, be.Pos.Y, be.Pos.Z);
            prog.Tex2D = capi.BlockTextureAtlas.AtlasTextures[0].TextureId;
            prog.ViewMatrix = rpi.CameraMatrixOriginf;
            prog.ProjectionMatrix = rpi.CurrentProjectionMatrix;

            float rot = RotY();
            foreach (var p in partes)
            {
                if (p.Show != null && !p.Show.Contains(modo)) continue;
                var mesh = brilha && p.On != null ? p.On : p.Off;
                if (mesh == null) continue;

                mat.Identity()
                    .Translate(be.Pos.X - cam.X, be.Pos.Y - cam.Y, be.Pos.Z - cam.Z)
                    .Translate(0.5f, 0, 0.5f).RotateYDeg(rot).Translate(-0.5f, 0, -0.5f)
                    .Translate(p.Pivo.X / 16f, p.Pivo.Y / 16f, p.Pivo.Z / 16f);

                foreach (var an in p.Anims)
                {
                    bool on = Ligado(an, modo);
                    if (an.When != null && !on) continue;
                    if (on) an.T += dt;
                    float t = an.T;
                    switch (an.Tipo)
                    {
                        case "spin": Girar(an.Eixo, t * (float.IsNaN(an.Speed) ? 2 : an.Speed)); break;
                        case "swing":
                            Girar(an.Eixo, on ? (float)Math.Sin(t * (float.IsNaN(an.Freq) ? 1 : an.Freq) * Math.PI * 2) * (float.IsNaN(an.Amp) ? 0.3f : an.Amp) : 0);
                            break;
                        case "shake":
                            Mover(an.Eixo, on ? (float)Math.Sin(t * (float.IsNaN(an.Freq) ? 3 : an.Freq) * Math.PI * 2) * (float.IsNaN(an.Amp) ? 0.5f : an.Amp) / 16f : 0);
                            break;
                        case "slide":
                            Mover(an.Eixo, on ? (t * (float.IsNaN(an.Speed) ? 0.3f : an.Speed) % 1f) * an.Dist / 16f : 0);
                            break;
                        case "bob":
                            Mover(an.Eixo, on ? ((float)Math.Sin(t * (float.IsNaN(an.Freq) ? 1 : an.Freq) * Math.PI * 2) * 0.5f + 0.5f) * (float.IsNaN(an.Amp) ? 2 : an.Amp) / 16f : 0);
                            break;
                        case "viagem":
                            {
                                float T = an.Periodo, f = (t % T) / T;
                                float Ease(float x) => x * x * (3 - 2 * x);
                                float k = f < 0.2f ? Ease(f / 0.2f) : f < 0.5f ? 1 : f < 0.7f ? 1 - Ease((f - 0.5f) / 0.2f) : 0;
                                Mover(an.Eixo, k * (float.IsNaN(an.Amp) ? 12 : an.Amp) / 16f);
                                break;
                            }
                    }
                }
                mat.Translate(-p.Pivo.X / 16f, -p.Pivo.Y / 16f, -p.Pivo.Z / 16f);
                prog.ModelMatrix = mat.Values;
                rpi.RenderMesh(mesh);
            }
            prog.Stop();
            rpi.GlEnableCullFace();
        }

        // O visualizador (three.js) usa rotação no sentido da regra da mão direita igual ao jogo
        void Girar(string eixo, float ang)
        {
            if (eixo == "x") mat.RotateX(ang);
            else if (eixo == "y") mat.RotateY(ang);
            else mat.RotateZ(ang);
        }

        void Mover(string eixo, float d)
        {
            if (eixo == "x") mat.Translate(d, 0, 0);
            else if (eixo == "y") mat.Translate(0, d, 0);
            else mat.Translate(0, 0, d);
        }

        public void Dispose()
        {
            foreach (var p in partes) { p.Off?.Dispose(); p.On?.Dispose(); }
            partes.Clear();
        }
    }
}
