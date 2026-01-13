"use client";

import { useState } from "react";
import {
  Users,
  UserCheck,
  UserPlus,
  UserMinus,
  TrendingUp,
  Calendar,
  LogOut,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";

interface Props {
  data: any;
  onReset: () => void;
}

export default function Dashboard({ data, onReset }: Props) {
  const [activeTab, setActiveTab] = useState<"overview" | "followers" | "following" | "relationships">("overview");

  const { snapshots, latestSnapshot, verification } = data;

  // Calculate metrics
  const totalSnapshots = snapshots.length;
  const followerCount = latestSnapshot?.follower_count || 0;
  const followingCount = latestSnapshot?.following_count || 0;

  // Calculate mutuals, not-following-back, not-followed-back
  const followersSet = new Set(latestSnapshot?.followers.map((f: any) => f.username) || []);
  const followingSet = new Set(latestSnapshot?.following.map((f: any) => f.username) || []);

  const mutuals = Array.from(followersSet).filter((u) => followingSet.has(u));
  const notFollowingBack = Array.from(followersSet).filter((u) => !followingSet.has(u));
  const notFollowedBack = Array.from(followingSet).filter((u) => !followersSet.has(u));

  // Calculate change from first snapshot
  let followerGrowth = 0;
  let followingGrowth = 0;
  if (snapshots.length > 1) {
    const oldest = snapshots[snapshots.length - 1];
    followerGrowth = followerCount - oldest.follower_count;
    followingGrowth = followingCount - oldest.following_count;
  }

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "followers", label: "Followers" },
    { id: "following", label: "Following" },
    { id: "relationships", label: "Relationships" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-instagram-text">
            Your Dashboard
          </h2>
          <p className="text-instagram-textSecondary mt-1">
            {totalSnapshots} snapshot{totalSnapshots !== 1 ? "s" : ""} loaded
          </p>
        </div>
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2 text-instagram-textSecondary hover:text-instagram-text transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Load Different Database
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-6 shadow-md border border-instagram-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-instagram-textSecondary text-sm">
              Followers
            </span>
            <Users className="w-5 h-5 text-instagram-blue" />
          </div>
          <div className="text-3xl font-bold text-instagram-text">
            {followerCount.toLocaleString()}
          </div>
          {followerGrowth !== 0 && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${followerGrowth > 0 ? "text-green-600" : "text-red-600"}`}>
              {followerGrowth > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              <span>{Math.abs(followerGrowth)} since first snapshot</span>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg p-6 shadow-md border border-instagram-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-instagram-textSecondary text-sm">
              Following
            </span>
            <UserPlus className="w-5 h-5 text-instagram-blue" />
          </div>
          <div className="text-3xl font-bold text-instagram-text">
            {followingCount.toLocaleString()}
          </div>
          {followingGrowth !== 0 && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${followingGrowth > 0 ? "text-green-600" : "text-red-600"}`}>
              {followingGrowth > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              <span>{Math.abs(followingGrowth)} since first snapshot</span>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg p-6 shadow-md border border-instagram-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-instagram-textSecondary text-sm">
              Mutuals
            </span>
            <UserCheck className="w-5 h-5 text-instagram-blue" />
          </div>
          <div className="text-3xl font-bold text-instagram-text">
            {mutuals.length.toLocaleString()}
          </div>
          <div className="text-sm text-instagram-textSecondary mt-2">
            {((mutuals.length / followerCount) * 100).toFixed(1)}% of followers
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-md border border-instagram-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-instagram-textSecondary text-sm">
              Snapshots
            </span>
            <Calendar className="w-5 h-5 text-instagram-blue" />
          </div>
          <div className="text-3xl font-bold text-instagram-text">
            {totalSnapshots}
          </div>
          <div className="text-sm text-instagram-textSecondary mt-2">
            {new Date(latestSnapshot.timestamp).toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md border border-instagram-border">
        <div className="border-b border-instagram-border">
          <div className="flex gap-1 p-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? "bg-instagram-bg text-instagram-text"
                    : "text-instagram-textSecondary hover:text-instagram-text"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {activeTab === "overview" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-instagram-text mb-4">
                  Snapshot History
                </h3>
                <div className="space-y-2">
                  {snapshots.map((snapshot: any, index: number) => (
                    <div
                      key={snapshot.id}
                      className="flex items-center justify-between p-4 bg-instagram-bg rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-instagram-blue text-white text-sm flex items-center justify-center">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-instagram-text">
                            {new Date(snapshot.timestamp).toLocaleDateString("en-US", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            })}
                          </p>
                          <p className="text-sm text-instagram-textSecondary">
                            {snapshot.source === "export" ? "Instagram Export" : "Graph API"}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-6 text-sm">
                        <div>
                          <span className="text-instagram-textSecondary">Followers: </span>
                          <span className="font-medium text-instagram-text">
                            {snapshot.follower_count}
                          </span>
                        </div>
                        <div>
                          <span className="text-instagram-textSecondary">Following: </span>
                          <span className="font-medium text-instagram-text">
                            {snapshot.following_count}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {Object.keys(verification).length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-instagram-text mb-4">
                    Verification Queue
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {Object.entries(verification).map(([status, count]) => (
                      <div key={status} className="p-3 bg-instagram-bg rounded-lg">
                        <p className="text-sm text-instagram-textSecondary capitalize">
                          {status}
                        </p>
                        <p className="text-2xl font-bold text-instagram-text">
                          {count as number}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === "followers" && (
            <div>
              <h3 className="text-lg font-semibold text-instagram-text mb-4">
                All Followers ({followerCount})
              </h3>
              <div className="grid md:grid-cols-2 gap-2 max-h-96 overflow-y-auto">
                {latestSnapshot?.followers.map((follower: any) => (
                  <div
                    key={follower.username}
                    className="flex items-center gap-3 p-3 bg-instagram-bg rounded-lg"
                  >
                    <div className="w-10 h-10 rounded-full bg-instagram-border flex items-center justify-center text-instagram-textSecondary font-medium">
                      {follower.username[0].toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-instagram-text truncate">
                        @{follower.username}
                      </p>
                      {follower.full_name && (
                        <p className="text-sm text-instagram-textSecondary truncate">
                          {follower.full_name}
                        </p>
                      )}
                    </div>
                    {followingSet.has(follower.username) && (
                      <span className="text-xs bg-instagram-blue text-white px-2 py-1 rounded-full">
                        Mutual
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "following" && (
            <div>
              <h3 className="text-lg font-semibold text-instagram-text mb-4">
                All Following ({followingCount})
              </h3>
              <div className="grid md:grid-cols-2 gap-2 max-h-96 overflow-y-auto">
                {latestSnapshot?.following.map((following: any) => (
                  <div
                    key={following.username}
                    className="flex items-center gap-3 p-3 bg-instagram-bg rounded-lg"
                  >
                    <div className="w-10 h-10 rounded-full bg-instagram-border flex items-center justify-center text-instagram-textSecondary font-medium">
                      {following.username[0].toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-instagram-text truncate">
                        @{following.username}
                      </p>
                      {following.full_name && (
                        <p className="text-sm text-instagram-textSecondary truncate">
                          {following.full_name}
                        </p>
                      )}
                    </div>
                    {followersSet.has(following.username) ? (
                      <span className="text-xs bg-instagram-blue text-white px-2 py-1 rounded-full">
                        Mutual
                      </span>
                    ) : (
                      <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full">
                        Not following back
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "relationships" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-instagram-text mb-4">
                  Mutuals ({mutuals.length})
                </h3>
                <p className="text-sm text-instagram-textSecondary mb-3">
                  Accounts that follow you and you follow back
                </p>
                <div className="grid md:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
                  {mutuals.map((username) => (
                    <div
                      key={username}
                      className="p-3 bg-green-50 border border-green-200 rounded-lg"
                    >
                      <p className="font-medium text-instagram-text truncate">
                        @{username}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-instagram-text mb-4">
                  Not Following Back ({notFollowingBack.length})
                </h3>
                <p className="text-sm text-instagram-textSecondary mb-3">
                  Accounts that follow you, but you don't follow them
                </p>
                <div className="grid md:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
                  {notFollowingBack.map((username) => (
                    <div
                      key={username}
                      className="p-3 bg-instagram-bg rounded-lg"
                    >
                      <p className="font-medium text-instagram-text truncate">
                        @{username}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-instagram-text mb-4">
                  Not Followed Back ({notFollowedBack.length})
                </h3>
                <p className="text-sm text-instagram-textSecondary mb-3">
                  Accounts you follow, but they don't follow you back
                </p>
                <div className="grid md:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
                  {notFollowedBack.map((username) => (
                    <div
                      key={username}
                      className="p-3 bg-red-50 border border-red-200 rounded-lg"
                    >
                      <p className="font-medium text-instagram-text truncate">
                        @{username}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
