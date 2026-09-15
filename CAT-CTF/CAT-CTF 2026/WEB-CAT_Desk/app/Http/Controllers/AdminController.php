<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class AdminController extends Controller
{
    public function __invoke(Request $request): View
    {
        $this->requireAdmin($request);

        return view('admin', [
            'users' => User::query()->orderBy('id')->get(),
            'adminMessage' => config('catdesk.admin_message'),
        ]);
    }

    public function flag(Request $request): JsonResponse
    {
        $this->requireAdmin($request);

        $flag = config('catdesk.flag');
        abort_unless(is_string($flag) && $flag !== '', 503);

        return response()->json(['flag' => $flag]);
    }

    private function requireAdmin(Request $request): void
    {
        abort_unless($request->user()?->is_admin === true, 403);
    }
}
