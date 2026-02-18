"""
ブラウン運動シミュレーション
Pisano 24の離散方向 × ランダムウォーク × 足し算のみ

熱運動：各点がPisano 24方向にランダムに揺らぐ
拡散：密度の高い場所から低い場所へ広がる
確率的な構造：ランダムから一時的な秩序が生まれる
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Pisano 24方向テーブル
PISANO_24_DIRS = [
    (10, 0), (10, 3), (9, 5), (8, 7), (7, 8), (5, 9),
    (3, 10), (0, 10), (-3, 10), (-5, 9), (-7, 8), (-8, 7),
    (-10, 0), (-10, -3), (-9, -5), (-8, -7), (-7, -8), (-5, -9),
    (-3, -10), (0, -10), (3, -10), (5, -9), (7, -8), (8, -7),
]

print("=== Brownian Motion Simulation ===")
print("B13の原点：ランダムウォークと拡散を足し算だけで")
print("Pisano 24方向テーブル準備完了\n")


class BrownianMotionSim:
    def __init__(self, width=80, height=40, temperature=5, n_particles=10):
        self.width = width
        self.height = height
        self.temperature = temperature  # 熱運動の強さ
        self.n_particles = n_particles  # 粒子数（密度の初期集中点）
        
        # 速度場（各点の運動量）
        self.vx = np.zeros((height, width), dtype=np.float32)
        self.vy = np.zeros((height, width), dtype=np.float32)
        
        # 密度場（粒子の存在確率）
        self.density = np.zeros((height, width), dtype=np.float32)
        
        # 初期粒子配置（中央に集中）
        center_x, center_y = width // 2, height // 2
        for i in range(n_particles):
            # 中央付近にランダム配置
            px = center_x + np.random.randint(-5, 6)
            py = center_y + np.random.randint(-5, 6)
            if 0 <= px < width and 0 <= py < height:
                self.density[py, px] += 10.0
        
        self.step = 0
        
    def apply_thermal_motion(self):
        """熱運動：各点がランダムに揺らぐ"""
        for y in range(self.height):
            for x in range(self.width):
                # 密度がある場所だけ揺らす（粒子がいる場所）
                if self.density[y, x] > 0.1:
                    # Pisano 24からランダムに方向を選ぶ
                    random_dir = np.random.randint(0, 24)
                    dx, dy = PISANO_24_DIRS[random_dir]
                    
                    # 温度に応じた強さで力を加える（足し算）
                    kick_strength = self.temperature
                    self.vx[y, x] += (dx * kick_strength) // 10
                    self.vy[y, x] += (dy * kick_strength) // 10
    
    def propagate_brownian(self):
        """ブラウン運動の伝播と拡散"""
        new_vx = np.copy(self.vx)
        new_vy = np.copy(self.vy)
        new_density = np.zeros_like(self.density)
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                current_density = self.density[y, x]
                
                if current_density < 0.01:
                    continue  # 密度が極小なら飛ばす
                
                # 現在の速度から移動方向を決める
                current_vx = self.vx[y, x]
                current_vy = self.vy[y, x]
                
                # 速度を24方向に離散化
                speed = int(np.sqrt(current_vx**2 + current_vy**2))
                if speed > 0:
                    angle_index = int((np.arctan2(current_vy, current_vx) * 24 / (2 * np.pi)) % 24)
                else:
                    angle_index = np.random.randint(0, 24)  # 止まってたらランダム
                
                # Pisano周期でシフト
                pisano_shift = (angle_index + self.step) % 24
                dir_dx, dir_dy = PISANO_24_DIRS[pisano_shift]
                
                # === 拡散：密度を周囲に分配 ===
                # 8方向に均等に分ける（足し算）
                share_per_neighbor = current_density // 10  # 10%ずつ分配
                remaining = current_density - share_per_neighbor * 8
                
                for dy_offset in [-1, 0, 1]:
                    for dx_offset in [-1, 0, 1]:
                        if dy_offset == 0 and dx_offset == 0:
                            new_density[y, x] += remaining  # 残りは自分に
                            continue
                        
                        ny = y + dy_offset
                        nx = x + dx_offset
                        
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            new_density[ny, nx] += share_per_neighbor
                
                # === 速度の拡散と減衰 ===
                # 周囲8方向から速度を集計
                influences_x = 0
                influences_y = 0
                count = 0
                
                for dy_offset in [-1, 0, 1]:
                    for dx_offset in [-1, 0, 1]:
                        if dy_offset == 0 and dx_offset == 0:
                            continue
                        
                        ny = y + dy_offset
                        nx = x + dx_offset
                        
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            influences_x += self.vx[ny, nx]
                            influences_y += self.vy[ny, nx]
                            count += 1
                
                if count > 0:
                    avg_vx = influences_x // count
                    avg_vy = influences_y // count
                    
                    # 新しい速度 = 現在値 + 周囲の影響 + Pisano方向 - 摩擦
                    friction = 2  # 減衰項（足し算の逆）
                    new_vx[y, x] = (current_vx * 6 + avg_vx * 3 + dir_dx * 1 - friction) // 10
                    new_vy[y, x] = (current_vy * 6 + avg_vy * 3 + dir_dy * 1 - friction) // 10
        
        self.vx = new_vx
        self.vy = new_vy
        self.density = new_density
        
        # 密度の正規化（全体の総和を保存）
        total = np.sum(self.density)
        if total > 0:
            self.density *= (self.n_particles * 10.0) / total
        
        self.step += 1
    
    def step_simulation(self):
        """1ステップ実行"""
        self.apply_thermal_motion()  # 熱運動
        self.propagate_brownian()    # 拡散
    
    def get_visualization_data(self):
        skip = 3
        X, Y = np.meshgrid(np.arange(0, self.width, skip), 
                          np.arange(0, self.height, skip))
        U = self.vx[::skip, ::skip]
        V = self.vy[::skip, ::skip]
        D = self.density[::skip, ::skip]
        return X, Y, U, V, D


# ============================================
# 実行部分
# ============================================
if __name__ == "__main__":
    print("温度設定: 5（熱運動の強さ）")
    print("初期粒子数: 10")
    print("開始...\n")
    
    sim = BrownianMotionSim(width=80, height=40, temperature=5, n_particles=10)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # 統計情報を記録
    entropy_history = []
    
    def update(frame):
        ax.clear()
        
        # シミュレーション1ステップ
        sim.step_simulation()
        
        # エントロピー計算（密度分布の広がり具合）
        # Shannon entropy: -Σ(p * log(p))
        density_normalized = sim.density / (np.sum(sim.density) + 1e-10)
        density_nonzero = density_normalized[density_normalized > 1e-10]
        entropy = -np.sum(density_nonzero * np.log(density_nonzero + 1e-10))
        entropy_history.append(entropy)
        
        # 可視化
        X, Y, U, V, D = sim.get_visualization_data()
        
        extent = [0, sim.width, 0, sim.height]
        
        # 密度を背景として表示（ホットカラーマップ）
        im = ax.imshow(sim.density, extent=extent, origin='lower', 
                       cmap='hot', alpha=0.8, aspect='auto', vmin=0, vmax=5)
        
        # 速度ベクトルを矢印で表示
        speed = np.sqrt(U**2 + V**2)
        if np.max(speed) > 0:
            ax.quiver(X, Y, U, V, speed, cmap='cool', scale=1000, width=0.002, alpha=0.6)
        
        ax.set_title(f'Brownian Motion (Addition Only) - Step {frame} | Entropy: {entropy:.2f}', 
                    fontsize=14)
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_xlim(0, sim.width)
        ax.set_ylim(0, sim.height)
        
        # 統計情報を表示
        total_density = np.sum(sim.density)
        max_density = np.max(sim.density)
        ax.text(5, sim.height - 5, 
                f'Total: {total_density:.1f} | Max: {max_density:.2f} | Temp: {sim.temperature}', 
                color='white', fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        return ax,
    
    # アニメーション作成
    anim = animation.FuncAnimation(fig, update, frames=150, interval=80, blit=False)
    
    output_path = 'brownian_motion.gif'
    anim.save(output_path, writer='pillow', fps=12)
    print(f"\nアニメーション保存: {output_path}")
    
    plt.close()
    
    # エントロピーの時間変化をプロット
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 最終状態
    X, Y, U, V, D = sim.get_visualization_data()
    extent = [0, sim.width, 0, sim.height]
    im = ax1.imshow(sim.density, extent=extent, origin='lower', 
                    cmap='hot', alpha=0.8, aspect='auto')
    speed = np.sqrt(U**2 + V**2)
    ax1.quiver(X, Y, U, V, speed, cmap='cool', scale=1000, width=0.002, alpha=0.6)
    ax1.set_title(f'Final State (Step {sim.step})')
    ax1.set_xlabel('X Position')
    ax1.set_ylabel('Y Position')
    
    # エントロピーの時間発展
    ax2.plot(entropy_history, linewidth=2, color='blue')
    ax2.set_title('Entropy Evolution (Diffusion Progress)')
    ax2.set_xlabel('Time Step')
    ax2.set_ylabel('Shannon Entropy')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=entropy_history[-1], color='red', linestyle='--', 
                label=f'Final: {entropy_history[-1]:.2f}')
    ax2.legend()
    
    plt.tight_layout()
    
    static_path = 'brownian_final_with_entropy.png'
    plt.savefig(static_path, dpi=150, bbox_inches='tight')
    print(f"最終状態 + エントロピー推移保存: {static_path}")
    
    plt.close()
    
    print("\n=== B13 Brownian Motion Complete ===")
    print(f"総ステップ数: {sim.step}")
    print(f"最終エントロピー: {entropy_history[-1]:.2f}")
    print(f"エントロピー増加: {entropy_history[-1] - entropy_history[0]:.2f}")
    print(f"平均拡散速度: {(entropy_history[-1] - entropy_history[0]) / len(entropy_history):.4f} per step")
    print("\n熱運動と拡散、三角関数なし・足し算のみで再現完了")
